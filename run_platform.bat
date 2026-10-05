@echo off
chcp 65001 > nul
echo =====================================================================
echo  NEN TANG THAM DINH ^& DOI CHUAN BDS PHUC VU TIN DUNG TRAI PHIEU
echo  Hanh lang: TP.HCM (vung ven) - Long An - Tay Ninh
echo =====================================================================
echo Dang khoi dong may chu giao dien Streamlit...
cd /d "%~dp0"
python -m streamlit run app.py
pause
