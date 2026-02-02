import logging
import sys
import io
import traceback

# Setup capture of logging
log_capture = io.StringIO()
handler = logging.StreamHandler(log_capture)
handler.setLevel(logging.WARNING)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.WARNING)

# Import the module
try:
    import mekhane.fep.derivative_selector as ds
except Exception:
    # If the module itself fails to import for some other reason
    print("Failed to import module")
    traceback.print_exc()
    sys.exit(1)

# Check GEMINI_AVAILABLE
if ds.GEMINI_AVAILABLE:
    print("GEMINI_AVAILABLE is True. This environment might have google.genai installed.")
    sys.exit(1)

# Check logs
log_contents = log_capture.getvalue()
print(f"Log contents: '{log_contents}'")

if "google.genai" in log_contents or "ImportError" in log_contents or "Gemini" in log_contents:
    print("Warning logged.")
else:
    print("No warning logged.")
