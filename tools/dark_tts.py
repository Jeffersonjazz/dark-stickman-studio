"""DARK TTS Engine — espeak-ng PT-BR, no external deps"""
import ctypes, wave, struct, os, re

LIB = '/usr/local/lib/python3.13/site-packages/espeakng_loader/libespeak-ng.so'
DATA = '/usr/local/lib/python3.13/site-packages/espeakng_loader/espeak-ng-data'

class EspeakEvent(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_int),
        ('unique_identifier', ctypes.c_uint),
        ('text_position', ctypes.c_int),
        ('length', ctypes.c_int),
        ('audio_position', ctypes.c_int),
        ('sample', ctypes.c_int),
        ('user_data', ctypes.c_void_p),
        ('id', ctypes.c_int),
    ]

SYNTH_CB_T = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_short),
    ctypes.c_int,
    ctypes.POINTER(EspeakEvent)
)

_lib = None
_cb = None
_samples = []

def _init_lib():
    global _lib, _cb
    if _lib is not None:
        return _lib
    lib = ctypes.CDLL(LIB)
    lib.espeak_Initialize.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
    lib.espeak_Initialize.restype = ctypes.c_int
    sr = lib.espeak_Initialize(1, 500, DATA.encode(), 0)  # 1=AUDIO_OUTPUT_RETRIEVAL
    if sr <= 0:
        raise RuntimeError(f"espeak_Initialize failed: sr={sr}")
    
    def synth_cb(wav, numsamples, events):
        if numsamples > 0 and wav:
            for i in range(numsamples):
                _samples.append(wav[i])
        return 0
    
    _cb = SYNTH_CB_T(synth_cb)
    lib.espeak_SetSynthCallback(_cb)
    
    lib.espeak_SetVoiceByName.argtypes = [ctypes.c_char_p]
    lib.espeak_SetVoiceByName.restype = ctypes.c_int
    
    lib.espeak_Synth.argtypes = [
        ctypes.c_char_p, ctypes.c_size_t,
        ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_uint,
        ctypes.POINTER(ctypes.c_uint), ctypes.c_void_p
    ]
    lib.espeak_Synth.restype = ctypes.c_int
    lib.espeak_Synchronize.argtypes = []
    lib.espeak_Synchronize.restype = ctypes.c_int
    
    lib.espeak_SetParameter.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
    lib.espeak_SetParameter.restype = ctypes.c_int
    
    lib._sr = sr
    _lib = lib
    return lib

def text_to_wav(text: str, output_path: str, voice: str = 'pt-br', 
               speed: int = 160, pitch: int = 50, volume: int = 100):
    """Convert text to WAV file using espeak PT-BR."""
    global _samples
    lib = _init_lib()
    
    # Set voice
    lib.espeak_SetVoiceByName(voice.encode())
    
    # Set parameters: 0=rate, 1=volume, 2=pitch, 3=range, 4=punctuation
    lib.espeak_SetParameter(0, speed, 0)   # rate (words/min), default=175
    lib.espeak_SetParameter(1, volume, 0)  # volume 0-200
    lib.espeak_SetParameter(2, pitch, 0)   # pitch 0-100, default=50
    lib.espeak_SetParameter(3, 50, 0)      # range 0-100
    
    # Clear samples
    _samples.clear()
    
    # Synthesize
    enc = text.encode('utf-8')
    r = lib.espeak_Synth(enc, len(enc)+1, 0, 0, 0, 1, None, None)
    lib.espeak_Synchronize()
    
    if not _samples:
        raise RuntimeError(f"No audio generated (r={r})")
    
    # Write WAV
    with wave.open(output_path, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(lib._sr)
        wf.writeframes(struct.pack(f'<{len(_samples)}h', *_samples))
    
    duration = len(_samples) / lib._sr
    print(f"[TTS] {len(_samples)} samples → {duration:.1f}s → {output_path}")
    return output_path, duration

def script_to_wav(script: str, output_path: str, style: str = 'mind'):
    """Convert full script to WAV with appropriate voice settings."""
    if style == 'horror':
        # Slower, lower pitch for Esquina do Medo
        return text_to_wav(script, output_path, voice='pt-br', speed=145, pitch=42, volume=100)
    else:
        # Normal for Mente de Aço
        return text_to_wav(script, output_path, voice='pt-br', speed=160, pitch=50, volume=100)

if __name__ == '__main__':
    # Quick test
    test_out = '/tmp/claude-0/-home-claude-dark-stickman-studio/b053b46d-0ed9-5042-b661-55c8cd85d5be/scratchpad/dark_tts_test.wav'
    text_to_wav("Bem-vindo ao Dark Studio. Sistema de síntese de voz ativo.", test_out)
    print(f"Test: {os.path.getsize(test_out)} bytes")
