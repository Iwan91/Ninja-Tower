#include <allegro5/allegro.h>
#include <allegro5/allegro_font.h>
#include <allegro5/allegro_ttf.h>
#include <allegro5/allegro_image.h>
#include <allegro5/allegro_primitives.h>
#include <allegro5/allegro_acodec.h>
#include <allegro5/allegro_audio.h>
#include "hero_simulation.h"
#include "shot_simulation.h"
#include "buff_simulation.h"
#include <vector>
#include <math.h>
using namespace std;
#pragma once 
class window
{
	public:
		int height;
		int width;
};


class map_fragment
{
	public:
		int x;
		int y;
};

class engine
{
	public:
        static engine& getInstance();
		void InitEngine();
		void PrepareStage();
		void MainLoopGame();

		window Window;
		map_fragment Map_fragment;
		vector<hero_simulation*> heroes_simulation;
		vector <shot_simulation*> shots_simulation;
		vector <buff_simulation*> buffs_simulation;
		int FPS;
		int old_ping;
		int enemy_kills;
		int ours_kills;
	private:
        engine();
        engine(const engine &);
        engine& operator=(const engine&);
		ALLEGRO_DISPLAY *display;
		ALLEGRO_EVENT_QUEUE *event_queue;
		ALLEGRO_TIMER *timer;
		void DrawMap();
		void DrawHeroes();
		void UpdateHeroFrames();
		void DrawDebugInfo();
		void InnerDebugInfo();
		void DrawHitBoxes();
		void NetworkUDP();
		void NetworkTCP();
		unsigned long iteration_udp;
		unsigned long iteration_client;
		void UpdateShotsFrames();
		void DrawShots();
		void CalculateCDs();

		void SendPing();
		int send_ping;
		int time_ping;
 };