#include <string>
#include <vector>
#include "Functions_HDD.h"
#include <allegro5/allegro.h>
#include <allegro5/allegro_font.h>
#include <allegro5/allegro_ttf.h>
#include <allegro5/allegro_image.h>
#include <allegro5/allegro_primitives.h>
#include <allegro5/allegro_acodec.h>
#include <allegro5/allegro_audio.h>
using namespace std;

#pragma once
class Platform
{
	public:
		int x1;
		int y;
		int width;
		int x2;
};

class Obstacle
{
	public:	
		int x1,y1;
		int x2,y2;
};

class SpawnTeam
{
	public:
		int x;
		int	y;
};

class Map
{
	public:
		vector<ALLEGRO_BITMAP*> pictures;
		bool load(string path);

		string MapName;
		int Height;
		int Width;
		vector<Platform> platforms;
		vector<Obstacle> obstacles;
		vector<SpawnTeam> spawnTeams;
		ALLEGRO_SAMPLE *sound;
};
