#ifndef INIREADER_H
#define INIREADER_H

#include "IniReader.h"
#include <iostream>
#include <Windows.h>
#include <string>
using namespace std;

class CIniReader
{
	public:
		 CIniReader(string szFileName); 
		 int ReadInteger(string szSection, string szKey, int iDefaultValue);
		 float ReadFloat(string szSection, string szKey, float fltDefaultValue);
		 bool ReadBoolean(string szSection, string szKey, bool bolDefaultValue);
		 string ReadString(string szSection, string szKey, string szDefaultValue);
	private:
		string m_szFileName;
};
#endif//INIREADER_H