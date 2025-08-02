import os
import sys
import logging

def configurar_logger():
    """
    Configura o logger da API com saída estruturada
    """

    logger = logging.getLogger("api_logger")
    logger.setLevel(logging.INFO)

    # Corrige múltiplos handlers ao recarregar o módulo
    if logger.handlers:
        return logger
        
    formatter = logging.Formatter(
        fmt='{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "msg": "%(message)s" }',
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    #Saída no terminal
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Saída para arquivo logs/api.log
    path_log = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    path_log = os.path.join(path_log, "logs")
    os.makedirs(path_log, exist_ok=True)    
    file_handler = logging.FileHandler(os.path.join(path_log, "api.log") , encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler
                      )
    return logger