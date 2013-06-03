#ifndef INIWRITER_H
#define INIWRITER_H

#include <string>
using namespace std;

class CIniWriter
{
public:
 CIniWriter(string szFileName); 
 void WriteInteger(string szSection, string szKey, int iValue);
 void WriteFloat(string szSection, string szKey, float fltValue);
 void WriteBoolean(string szSection, string szKey, bool bolValue);
 void WriteString(string szSection, string szKey, string szValue);
private:
	string m_szFileName;
};
#endif //INIWRITER_H