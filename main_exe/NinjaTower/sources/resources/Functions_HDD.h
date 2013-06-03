#include <fstream>
#include <vector>
#include "dirent.h"
#include <string>
using namespace std;

#pragma once
class Functions_HDD
{
	public:
		static bool FileExists( const char* FileName );
		static vector<string> ListOfDirectories(string path);
		static vector<string> ListOfFiles(string path);
		static vector<string> ListOfDirectoriesAndFiles(string path);
		static vector<string> Find(string path, string whatFind);
		static string IntToStr(int n);
};



