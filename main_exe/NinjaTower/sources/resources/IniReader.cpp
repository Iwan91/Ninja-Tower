#include "IniReader.h"

CIniReader::CIniReader(string szFileName)
{
	m_szFileName=szFileName;
}
int CIniReader::ReadInteger(string szSection, string szKey, int iDefaultValue)
{
	int iResult = GetPrivateProfileInt(szSection.c_str(),  szKey.c_str(), iDefaultValue, m_szFileName.c_str()); 
	return iResult;
}
float CIniReader::ReadFloat(string szSection, string szKey, float fltDefaultValue)
{
	 char szResult[255];
	 char szDefault[255];
	 float fltResult;
	 sprintf(szDefault, "%f",fltDefaultValue);
	 GetPrivateProfileString(szSection.c_str(),  szKey.c_str(), szDefault, szResult, 255, m_szFileName.c_str()); 
	 fltResult =  atof(szResult);
	 return fltResult;
}
bool CIniReader::ReadBoolean(string szSection, string szKey, bool bolDefaultValue)
{
	 char szResult[255];
	 char szDefault[255];
	 bool bolResult;
	 sprintf(szDefault, "%s", bolDefaultValue? "True" : "False");
	 GetPrivateProfileString(szSection.c_str(), szKey.c_str(), szDefault, szResult, 255, m_szFileName.c_str()); 
	 bolResult =  (strcmp(szResult, "True") == 0 || strcmp(szResult, "true") == 0) ? true : false;
	 return bolResult;
}
string CIniReader::ReadString(string szSection, string szKey, string szDefaultValue)
{
	 char* szResult = new char[255];
	 memset(szResult, 0x00, 255);
	 GetPrivateProfileString(szSection.c_str(),  szKey.c_str(), szDefaultValue.c_str(), szResult, 255, m_szFileName.c_str()); 
	 return szResult;
}