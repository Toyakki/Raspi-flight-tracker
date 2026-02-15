class OpenSkyError(RuntimeError):
    """Base error for OpenSky API faiures."""
    pass
    
class OpenSkyDeprecated(OpenSkyError):
    """Raised when the endpoint is gone/deprecated."""
    pass

class AdsdbError(RuntimeError):
    """Base error for ADSDB API faiures."""
    pass