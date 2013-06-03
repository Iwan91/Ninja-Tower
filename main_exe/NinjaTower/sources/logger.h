#include <string>
#include <fstream>
#include <time.h>
#include <iostream>
using namespace std;
#pragma once
class logger
{
	public:
		static void start_logging(int type_of_log);
		static enum level
		{
			info=0,
			debug=1,
			exception=2,
			warning=3,
			error=4,
			fatal_error=5
		};
		
		static void Write(string message,level level);
		static void Write(string message);
	private:
		static int type_of_log;
		static string file_name;
		static string level_string[];
};