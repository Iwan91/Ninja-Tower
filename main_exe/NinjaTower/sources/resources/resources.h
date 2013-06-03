#include "game_info.h"
#include <allegro5/allegro.h>
#include <allegro5/allegro_font.h>
#include <allegro5/allegro_ttf.h>
#include <allegro5/allegro_image.h>
#include <allegro5/allegro_primitives.h>
#include "Map.h"
#include "Hero.h"
#include <vector>
#include "../engine/engine.h"
#include <string>
using namespace std;
#pragma once
class resources
{
	public:
		static resources& getInstance();
		game_info game_info;
		Map map;
		vector <Hero*> heroes;
		vector <Shot*> shots;
		vector <Buff*> buffs;
		void LoadResources();
		struct fonts
		{
			ALLEGRO_FONT *font48;
			ALLEGRO_FONT *font12;

			ALLEGRO_FONT *font25;
			ALLEGRO_FONT *font20;
			ALLEGRO_FONT *font15;
			ALLEGRO_FONT *font16;
			ALLEGRO_FONT *font11;
		}Fonts;

		struct gui
		{
			ALLEGRO_BITMAP *avatar_dead;
			ALLEGRO_BITMAP *ball_enemy;
			ALLEGRO_BITMAP *ball_friend;
			ALLEGRO_BITMAP *bottom_active_skill;
			ALLEGRO_BITMAP *bottom_body;
			ALLEGRO_BITMAP *bottom_text;
			ALLEGRO_BITMAP *frame_enemy;
			ALLEGRO_BITMAP *frame_friend;
			ALLEGRO_BITMAP *frame_player;
			ALLEGRO_BITMAP *hp_g_body;
			ALLEGRO_BITMAP *hp_g_end;
			ALLEGRO_BITMAP *hp_g_start;
			ALLEGRO_BITMAP *hp_r_body;
			ALLEGRO_BITMAP *hp_r_end;
			ALLEGRO_BITMAP *hp_r_start;
			ALLEGRO_BITMAP *hp_y_body;
			ALLEGRO_BITMAP *hp_y_end;
			ALLEGRO_BITMAP *hp_y_start;
			ALLEGRO_BITMAP *minihp_g;
			ALLEGRO_BITMAP *minihp_r;
			ALLEGRO_BITMAP *minihp_y;
			ALLEGRO_BITMAP *nametag_body;
			ALLEGRO_BITMAP *nametag_end;
			ALLEGRO_BITMAP *nametag_start;
			ALLEGRO_BITMAP *score;
			ALLEGRO_BITMAP *bottom_cd_skill;
		} Gui;
		ALLEGRO_BITMAP *splash;
		ALLEGRO_BITMAP *win;
		ALLEGRO_BITMAP *lose;

	private:
		resources();
        resources(const resources &);
        resources& operator=(const resources&);
		bool LoadResourcesFont();
		bool LoadResourcesHeroes();
		bool LoadResourcesMaps();
		bool LoadResourcesShots();
		bool LoadResourcesBuffs();
		bool LoadGui();
		void splashInfo(string text);

  
};
