#include "logger.h"

int logger::type_of_log=3;
string logger::file_name="";
string logger::level_string[]={"0 info","1 debug","2 exception","3 warning","4 error","5 fatal_error"};

void logger::start_logging(int type_of_log)
{
	logger::type_of_log=type_of_log;

	time_t rawtime;
	struct tm * timeinfo;
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	char output[30];
    strftime(output, 30,"%d_%m_%Y %H_%M_%S", timeinfo);
	
	logger::file_name="Logs\\"+string(output)+".txt";

	ofstream myfile(file_name.c_str(),ios::out|ios::app);
	myfile.close();
}

void logger::Write(string message)
{
	ofstream myfile(file_name.c_str(),ios::out|ios::app);
	myfile<<message<<endl;
	myfile.close();
}

void logger::Write(string message, level level)
{
	time_t rawtime;
	struct tm * timeinfo;
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	char output[30];
    strftime(output, 30,"%d_%m_%Y %H_%M_%S", timeinfo);

	string save=string(output)+" "+logger::level_string[level]+" "+message;
	
	if(type_of_log==1 || type_of_log==3)
	{
		clog<<save<<endl;
	}

	if(type_of_log==2 || type_of_log==3)
	{
		ofstream myfile(file_name.c_str(),ios::out|ios::app);
		myfile<<save<<endl;
		myfile.close();
	}
	
}
