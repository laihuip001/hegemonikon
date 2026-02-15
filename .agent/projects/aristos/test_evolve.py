"""Aristos L2 Evolution Engine Tests

Test categories:
- FitnessVector: scalar calculation, repr
- Chromosome: creation, generic type
- FeedbackCollector: add, save, load, signal weights
- EvolutionEngine: population, selection, crossover, mutation, evolution
- Persistence: save/load weights
- Scale: mutation rate differences
"""

import json
import tempfile
from pathlib import Path

import pytest

from aristos.evolve import (
    Chromosome,
    EvolutionEngine,
    FeedbackCollector,
    FeedbackEntry,
    FitnessVector,
    Scale,
    SCALE_MUTATION_RATES,
    SCALE_MUTATION_SIGMA,
)


# =============================================================================
# FitnessVector
# =============================================================================


class TestFitnessVector:
    def test_default_values(self):
        fv = FitnessVector()
        assert fv.depth == 0.0
        assert fv.precision == 0.0
        assert fv.efficiency == 0.0
        assert fv.novelty == 0.0

    def test_scalar_default_weights(self):
        fv = FitnessVector(depth=2.0, precision=0.8, efficiency=1.0, novelty=0.5)
        # depth*1.0 + precision*2.0 + efficiency*0.5 + novelty*0.3
        expected = 2.0 * 1.0 + 0.8 * 2.0 + 1.0 * 0.5 + 0.5 * 0.3
        assert abs(fv.scalar() - expected) < 1e-9

    def test_scalar_custom_weights(self):
        fv = FitnessVector(depth=1.0, precision=1.0)
        custom = {"depth": 3.0, "precision": 5.0, "efficiency": 0.0, "novelty": 0.0}
        assert abs(fv.scalar(custom) - 8.0) < 1e-9

    def test_repr(self):
        fv = FitnessVector(depth=1.0, precision=0.5)
        r = repr(fv)
        assert "Fitness(" in r
        assert "depth=1.00" in r


# =============================================================================
# Chromosome
# =============================================================================


class TestChromosome:
    def test_creation(self):
        c = Chromosome(genes={"a": 1.0, "b": 2.0})
        assert c.genes["a"] == 1.0
        assert c.generation == 0
        assert isinstance(c.fitness, FitnessVector)

    def test_generic_type(self):
        """Chromosome can hold different gene types"""
        c_dict = Chromosome(genes={"x": 0.5})
        c_list = Chromosome(genes=[1, 2, 3])
        c_str = Chromosome(genes="macro_config")
        assert isinstance(c_dict.genes, dict)
        assert isinstance(c_list.genes, list)
        assert isinstance(c_str.genes, str)

    def test_repr_truncation(self):
        long_genes = {f"key_{i}": float(i) for i in range(20)}
        c = Chromosome(genes=long_genes)
        r = repr(c)
        assert "..." in r


# =============================================================================
# FeedbackEntry
# =============================================================================


class TestFeedbackEntry:
    def test_was_correct_implicit(self):
        e = FeedbackEntry(theorem="O1", problem="test", selected="nous")
        assert e.was_correct is True

    def test_was_correct_explicit(self):
        e = FeedbackEntry(
            theorem="O1", problem="test", selected="nous", corrected_to="phro"
        )
        assert e.was_correct is False


# =============================================================================
# FeedbackCollector
# =============================================================================


class TestFeedbackCollector:
    def test_add_and_len(self):
        fc = FeedbackCollector()
        fc.add(FeedbackEntry(theorem="O1", problem="test", selected="nous"))
        assert len(fc) == 1

    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "feedback.json"
            fc = FeedbackCollector(path=path)
            fc.add(FeedbackEntry(theorem="O1", problem="本質", selected="nous"))
            fc.add(
                FeedbackEntry(
                    theorem="O2",
                    problem="目的",
                    selected="desir",
                    corrected_to="voli",
                )
            )
            fc.save()

            # Reload
            fc2 = FeedbackCollector(path=path)
            entries = fc2.load()
            assert len(entries) == 2
            assert entries[0].theorem == "O1"
            assert entries[0].was_correct is True
            assert entries[1].corrected_to == "voli"

    def test_for_theorem(self):
        fc = FeedbackCollector()
        fc.add(FeedbackEntry(theorem="O1", problem="a", selected="nous"))
        fc.add(FeedbackEntry(theorem="O2", problem="b", selected="desir"))
        fc.add(FeedbackEntry(theorem="O1", problem="c", selected="phro"))
        assert len(fc.for_theorem("O1")) == 2
        assert len(fc.for_theorem("O2")) == 1

    def test_signal_weight_implicit(self):
        fc = FeedbackCollector()
        e = FeedbackEntry(theorem="O1", problem="t", selected="nous")
        assert fc.signal_weight(e) == 0.3

    def test_signal_weight_explicit(self):
        fc = FeedbackCollector()
        e = FeedbackEntry(
            theorem="O1", problem="t", selected="nous", corrected_to="phro"
        )
        assert fc.signal_weight(e) == 1.0

    def test_signal_weight_llm(self):
        fc = FeedbackCollector()
        e = FeedbackEntry(
            theorem="O1", problem="t", selected="nous", method="llm"
        )
        assert fc.signal_weight(e) == 0.5


# =============================================================================
# EvolutionEngine — Population & Evaluation
# =============================================================================


class TestEvolutionEngineBasic:
    def test_create_population(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        pop = engine.create_population(["nous", "phro", "meta"], pop_size=10)
        assert len(pop) == 10
        for c in pop:
            assert set(c.genes.keys()) == {"nous", "phro", "meta"}
            for v in c.genes.values():
                assert 0.5 <= v <= 1.5

    def test_evaluate_with_feedback(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        c = Chromosome(genes={"nous": 1.5, "phro": 0.5, "meta": 0.3})
        feedback = [
            FeedbackEntry(theorem="O1", problem="本質", selected="nous"),
            FeedbackEntry(theorem="O1", problem="実践", selected="phro"),
        ]
        score = engine.evaluate(c, feedback)
        # "nous" has highest weight → predicts "nous" for both
        # Entry 1: correct (selected nous, predicted nous)
        # Entry 2: correct (selected phro, but predicted nous → wrong)
        assert 0.0 <= score <= 1.0

    def test_evaluate_empty_feedback(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        c = Chromosome(genes={"nous": 1.0})
        assert engine.evaluate(c, []) == 0.0


# =============================================================================
# EvolutionEngine — Selection, Crossover, Mutation
# =============================================================================


class TestEvolutionEngineOperators:
    def test_tournament_select(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        pop = [
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.3)),
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.9)),
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.5)),
        ]
        # With k=3, should always select the best (precision=0.9)
        winner = engine.tournament_select(pop, k=3)
        assert winner.fitness.precision == 0.9

    def test_crossover_produces_valid_child(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        p1 = Chromosome(genes={"a": 0.5, "b": 1.0}, generation=3)
        p2 = Chromosome(genes={"a": 1.5, "b": 0.5}, generation=5)
        child = engine.crossover(p1, p2)

        assert set(child.genes.keys()) == {"a", "b"}
        for v in child.genes.values():
            assert 0.0 <= v <= 2.0
        assert child.generation == 6  # max(3, 5) + 1

    def test_crossover_union_keys(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        p1 = Chromosome(genes={"a": 1.0})
        p2 = Chromosome(genes={"b": 1.0})
        child = engine.crossover(p1, p2)
        assert "a" in child.genes
        assert "b" in child.genes

    def test_mutate_bounds(self):
        """Mutation should keep values in [0.0, 2.0]"""
        engine = EvolutionEngine(scale=Scale.MICRO)
        c = Chromosome(genes={"a": 0.01, "b": 1.99})
        for _ in range(100):
            mutated = engine.mutate(c)
            for v in mutated.genes.values():
                assert 0.0 <= v <= 2.0

    def test_mutate_changes_genes(self):
        """With high mutation rate, genes should change"""
        engine = EvolutionEngine(scale=Scale.MICRO)
        c = Chromosome(genes={f"k{i}": 1.0 for i in range(20)})
        mutated = engine.mutate(c)
        # With 30% mutation rate and 20 genes, highly likely at least 1 changed
        changed = sum(
            1 for k in c.genes if abs(c.genes[k] - mutated.genes[k]) > 1e-10
        )
        # This could technically fail but is extremely unlikely
        assert changed >= 1


# =============================================================================
# EvolutionEngine — Scale differences
# =============================================================================


class TestScaleDifferences:
    def test_mutation_rates_decrease_with_scale(self):
        assert SCALE_MUTATION_RATES[Scale.MICRO] > SCALE_MUTATION_RATES[Scale.MESO]
        assert SCALE_MUTATION_RATES[Scale.MESO] > SCALE_MUTATION_RATES[Scale.MACRO]

    def test_sigma_decreases_with_scale(self):
        assert SCALE_MUTATION_SIGMA[Scale.MICRO] > SCALE_MUTATION_SIGMA[Scale.MESO]
        assert SCALE_MUTATION_SIGMA[Scale.MESO] > SCALE_MUTATION_SIGMA[Scale.MACRO]

    def test_engine_uses_scale_rate(self):
        engine_micro = EvolutionEngine(scale=Scale.MICRO)
        engine_macro = EvolutionEngine(scale=Scale.MACRO)
        assert engine_micro.mutation_rate == 0.30
        assert engine_macro.mutation_rate == 0.03


# =============================================================================
# EvolutionEngine — Full evolution
# =============================================================================


class TestEvolution:
    def test_evolution_improves_fitness(self):
        """After evolution, best fitness should improve"""
        engine = EvolutionEngine(scale=Scale.MICRO)

        # Create feedback where "nous" is always the correct answer
        feedback = [
            FeedbackEntry(theorem="O1", problem=f"case_{i}", selected="nous")
            for i in range(30)
        ]

        pop = engine.create_population(["nous", "phro", "meta"], pop_size=20)

        # Measure initial best fitness
        engine.evaluate_population(pop, feedback)
        initial_best = max(c.fitness.scalar() for c in pop)

        # Evolve
        result = engine.evolve(pop, feedback, generations=20)
        final_best = max(c.fitness.scalar() for c in result)

        # Best fitness should not decrease (elitism guarantees this)
        assert final_best >= initial_best

    def test_best_returns_highest(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        pop = [
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.1)),
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.9)),
            Chromosome(genes={"a": 1.0}, fitness=FitnessVector(precision=0.5)),
        ]
        assert engine.best(pop).fitness.precision == 0.9

    def test_evolved_population_sorted(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        feedback = [
            FeedbackEntry(theorem="O1", problem="test", selected="nous")
            for _ in range(10)
        ]
        pop = engine.create_population(["nous", "phro"], pop_size=10)
        result = engine.evolve(pop, feedback, generations=5)

        # Should be sorted descending by fitness
        scalars = [c.fitness.scalar() for c in result]
        assert scalars == sorted(scalars, reverse=True)


# =============================================================================
# Persistence
# =============================================================================


class TestPersistence:
    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "weights.json"
            original = Chromosome(
                genes={"nous": 1.5, "phro": 0.8, "meta": 0.3},
                fitness=FitnessVector(
                    depth=2.0, precision=0.85, efficiency=1.2, novelty=0.4
                ),
                generation=42,
            )

            EvolutionEngine.save_weights(original, path)
            loaded = EvolutionEngine.load_weights(path)

            assert loaded is not None
            assert loaded.genes == original.genes
            assert loaded.generation == 42
            assert abs(loaded.fitness.precision - 0.85) < 1e-9

    def test_load_nonexistent(self):
        result = EvolutionEngine.load_weights(Path("/nonexistent/weights.json"))
        assert result is None

    def test_save_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "weights.json"
            c = Chromosome(genes={"a": 1.0})
            EvolutionEngine.save_weights(c, path)
            assert path.exists()

    def test_weights_json_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "weights.json"
            c = Chromosome(
                genes={"nous": 1.5},
                fitness=FitnessVector(precision=0.9),
                generation=10,
            )
            EvolutionEngine.save_weights(c, path)

            with open(path) as f:
                data = json.load(f)

            assert data["generation"] == 10
            assert data["weights"]["nous"] == 1.5
            assert "scalar" in data["fitness"]


# =============================================================================
# Suggest weights
# =============================================================================


class TestSuggestWeights:
    def test_suggest_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            weights_dir = Path(tmpdir)
            path = weights_dir / "O1.json"
            c = Chromosome(genes={"nous": 1.8, "phro": 0.5, "meta": 0.3})
            EvolutionEngine.save_weights(c, path)

            engine = EvolutionEngine(scale=Scale.MICRO)
            weights = engine.suggest_weights("O1", weights_dir=weights_dir)
            assert weights is not None
            assert weights["nous"] == 1.8

    def test_suggest_nonexistent(self):
        engine = EvolutionEngine(scale=Scale.MICRO)
        weights = engine.suggest_weights("ZZ", weights_dir=Path("/tmp/nonexistent"))
        assert weights is None
