#include "game.h"

game::game()
{
}

void game::run(int argc, char **argv)
{
	//argv[1] -login
	//argv[2] -haslo
	//argv[3] -ip
	//argv[4] -TCP
	//argv[5] -UDP 
	//argv[6] -debug on screen; 1-true; 0-false;
	//argv[7] -log; 0-no log; 1-log on console; 2-log to file; 3-log to console and file
	try
	{
		if(argc==8)
		{
			debug=atoi(argv[6]);
			logger::start_logging(atoi(argv[7]));
			logger::Write(argv[0],logger::level::debug);
			logger::Write("start parameters: OK",logger::level::debug);
			communication::getInstance().SetConnection(argv[1],argv[2],argv[3],argv[4],argv[5]);
			communication::getInstance().Connect();
			logger::Write("Secure TCP: OK",logger::level::debug);

			engine::getInstance().InitEngine();
			resources::getInstance().LoadResources();
			communication::getInstance().SendReady();
			communication::getInstance().ReceiveTCP();
			communication::getInstance().TCPNonBlocking(1);
			engine::getInstance().MainLoopGame();
		}
		else 
		{
			logger::Write("too much/less parameters at start game",logger::level::fatal_error);
		}	
	}
	catch (std::string exception)
	{
		logger::Write(exception,logger::level::exception);
	}
}

game& game::getInstance()
{
	//Inicjalizacja statycznego obiektu.
    //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
    //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
    //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
	static game instance;
	return instance;
}
