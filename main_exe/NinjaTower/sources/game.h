#include "logger.h"
#include "sockets/communication.h"
#include "resources/resources.h"
#include "engine/engine.h"
using namespace std;
#pragma once
class game
 {
	public:
		static game& getInstance();
		void run(int argc, char **argv);
		int debug;
	private:
		game();
		game(const game &);
		game& operator=(const game&);
};