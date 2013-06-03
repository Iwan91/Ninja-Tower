#include "Functions_HDD.h"

bool Functions_HDD::FileExists( const char* FileName )
{
    FILE* fp = NULL;

    //will not work if you do not have read permissions

    //to the file, but if you don''t have read, it

    //may as well not exist to begin with.

    fp = fopen( FileName, "rb" );
    if( fp != NULL )
    {
        fclose( fp );
        return true;
    }

    return false;
}


vector<string> Functions_HDD::ListOfDirectories(string path)
{
	DIR *Dir;
	struct dirent *DirEntry;
	vector<string> wynik;
	Dir = opendir (path.c_str());

	if (Dir != NULL)
	{
	  DirEntry=readdir(Dir);
	  DirEntry=readdir(Dir);
	  while ((DirEntry=readdir(Dir))!= NULL)
	  {
		string name=DirEntry->d_name;
		if(name.find(".")==string::npos)
		{
			wynik.push_back(DirEntry->d_name);
		}
	  }
	  closedir (Dir);
	}
	return wynik;
}

vector<string> Functions_HDD::ListOfFiles(string path)
{
	DIR *Dir;
	struct dirent *DirEntry;
	vector<string> wynik;
	Dir = opendir (path.c_str());

	if (Dir != NULL)
	{
	  DirEntry=readdir(Dir);
	  DirEntry=readdir(Dir);
	  while ((DirEntry=readdir(Dir))!= NULL)
	  {
		string name=DirEntry->d_name;
		if(name.find(".")!=string::npos)
		{
			wynik.push_back(DirEntry->d_name);
		}
	  }
	  closedir (Dir);
	}
	return wynik;
}

vector<string> Functions_HDD::ListOfDirectoriesAndFiles(string path)
{
	DIR *Dir;
	struct dirent *DirEntry;
	vector<string> wynik;
	Dir = opendir (path.c_str());

	if (Dir != NULL)
	{
	  DirEntry=readdir(Dir);
	  DirEntry=readdir(Dir);
	  while ((DirEntry=readdir(Dir))!= NULL)
	  {
	  	wynik.push_back(DirEntry->d_name);
	  }
	  closedir (Dir);
	}
	return wynik;
}

vector<string> Functions_HDD::Find(string path, string whatFind)
{
	DIR *Dir;
	struct dirent *DirEntry;
	vector<string> wynik;
	Dir = opendir (path.c_str());

	if (Dir != NULL)
	{
	  DirEntry=readdir(Dir);
	  DirEntry=readdir(Dir);
	  while ((DirEntry=readdir(Dir))!= NULL)
	  {
		string name=DirEntry->d_name;
		if(name.find(whatFind)!=string::npos)
		{
			wynik.push_back(DirEntry->d_name);
		}
	  }
	  closedir (Dir);
	}
	return wynik;
}
string Functions_HDD::IntToStr(int n)
{
     string tmp, ret;
     if(n < 0) {
          ret = "-";
          n = -n;
     }
     do {
          tmp += n % 10 + 48;
          n -= n % 10;
     }
     while(n /= 10);
     for(int i = tmp.size()-1; i >= 0; i--)
          ret += tmp[i];
     return ret;
}