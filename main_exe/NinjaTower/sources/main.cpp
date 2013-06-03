#include "game.h"
void main(int argc, char **argv)
{
	//MessageBox(NULL, "Hello", NULL, NULL);
	game::getInstance().run(argc,argv);
}
