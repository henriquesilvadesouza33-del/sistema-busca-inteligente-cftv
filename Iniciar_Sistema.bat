@echo off
title PROJETO SCHUBERT INVESTIGACAO - NOVACAP
cls

echo ===================================================
echo     INICIALIZANDO ASSISTENTE VIRTUAL (NOVACAP)     
echo ===================================================
echo.
echo [SISTEMA] Verificando integridade das dependencias...

:: Garante que as bibliotecas necessarias estao instaladas
python -m pip install opencv-python pillow cvzone pyttsx3 --quiet

echo [SISTEMA] Protocolo Stark ativo. Carregando interface...
echo.

:: Executa o script Python
python Schubert_investigation.py

echo.
echo ===================================================
echo            SISTEMA ENCERRADO COM SUCESSO           
echo ===================================================
pause
