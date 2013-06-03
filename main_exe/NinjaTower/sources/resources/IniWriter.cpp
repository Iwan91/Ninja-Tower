#include "IniWriter.h"
#include <iostream>
#include <Windows.h> 
CIniWriter::CIniWriter(string szFileName)
{
	m_szFileName=szFileName;
}
void CIniWriter::WriteInteger(string szSection, string szKey, int iValue)
{
	 char szValue[255];
	 sprintf(szValue, "%d", iValue);
	 WritePrivateProfileString(szSection.c_str(),  szKey.c_str(), szValue, m_szFileName.c_str()); 
}
void CIniWriter::WriteFloat(string szSection, string szKey, float fltValue)
{
	 char szValue[255];
	 sprintf(szValue, "%f", fltValue);
	 WritePrivateProfileString(szSection.c_str(),  szKey.c_str(), szValue, m_szFileName.c_str()); 
}
void CIniWriter::WriteBoolean(string szSection, string szKey, bool bolValue)
{
	 char szValue[255];
	 sprintf(szValue, "%s", bolValue ? "True" : "False");
	 WritePrivateProfileString(szSection.c_str(),  szKey.c_str(), szValue, m_szFileName.c_str()); 
}
void CIniWriter::WriteString(string szSection, string szKey, string szValue)
{
	WritePrivateProfileString(szSection.c_str(),  szKey.c_str(), szValue.c_str(), m_szFileName.c_str());
}