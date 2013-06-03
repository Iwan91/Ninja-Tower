#include "resources.h"
#include "../game.h"


resources::resources()
{
}

resources&  resources::getInstance()
{
          //Inicjalizacja statycznego obiektu.
          //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
          //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
          //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
          static resources instance;
          return instance;
}

void resources::LoadResources()
{
	splash=al_load_bitmap("data\\LoadingScreen.jpg");
	if(!splash){logger::Write("LoadingScreen.jpg==NULL",logger::level::fatal_error);exit(0);};

	
	//load fonts
	if(LoadResourcesFont()==false) exit(0);

	splashInfo("Loading gui...");
	if(LoadGui()==false) exit(0);

	splashInfo("Loading heroes...");
	if(LoadResourcesHeroes()==false) exit(0);

	splashInfo("Loading shots...");
	if(LoadResourcesShots()==false) exit(0);

	splashInfo("Loading buffs...");
	if(LoadResourcesBuffs()==false) exit(0);

	splashInfo("Loading map...");
	if(LoadResourcesMaps()==false) exit(0);

	splashInfo("Create game stage...");
	engine::getInstance().PrepareStage();

	splashInfo("Waiting for others...");

}
bool resources::LoadGui()
{
	string path="data\\gui\\";
	Gui.avatar_dead=al_load_bitmap((path+"avatar_dead.png").c_str());
	if(!Gui.avatar_dead){logger::Write("avatar_dead.png==NULL",logger::level::fatal_error);return false;};

	Gui.ball_enemy=al_load_bitmap((path+"ball_enemy.png").c_str());
	if(!Gui.ball_enemy){logger::Write("ball_enemy.png==NULL",logger::level::fatal_error);return false;};

	Gui.ball_friend=al_load_bitmap((path+"ball_friend.png").c_str());
	if(!Gui.ball_friend){logger::Write("ball_friend.png==NULL",logger::level::fatal_error);return false;};

	Gui.bottom_active_skill=al_load_bitmap((path+"bottom_active_skill.png").c_str());
	if(!Gui.bottom_active_skill){logger::Write("bottom_active_skill.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.bottom_body=al_load_bitmap((path+"bottom_body.png").c_str());
	if(!Gui.bottom_body){logger::Write("bottom_body.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.bottom_text=al_load_bitmap((path+"bottom_text.png").c_str());
	if(!Gui.bottom_text){logger::Write("bottom_text.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.frame_enemy=al_load_bitmap((path+"frame_enemy.png").c_str());
	if(!Gui.frame_enemy){logger::Write("frame_enemy.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.frame_friend=al_load_bitmap((path+"frame_friend.png").c_str());
	if(!Gui.frame_friend){logger::Write("frame_friend.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.frame_player=al_load_bitmap((path+"frame_player.png").c_str());
	if(!Gui.frame_player){logger::Write("frame_player.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_g_body=al_load_bitmap((path+"hp_g_body.png").c_str());
	if(!Gui.hp_g_body){logger::Write("hp_g_body.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_g_end=al_load_bitmap((path+"hp_g_end.png").c_str());
	if(!Gui.hp_g_end){logger::Write("hp_g_end.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_g_start=al_load_bitmap((path+"hp_g_start.png").c_str());
	if(!Gui.hp_g_start){logger::Write("hp_g_start.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_r_body=al_load_bitmap((path+"hp_r_body.png").c_str());
	if(!Gui.hp_r_body){logger::Write("hp_r_body.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_r_end=al_load_bitmap((path+"hp_r_end.png").c_str());
	if(!Gui.hp_r_end){logger::Write("hp_r_end.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_r_start=al_load_bitmap((path+"hp_r_start.png").c_str());
	if(!Gui.hp_r_start){logger::Write("hp_r_start.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_y_body=al_load_bitmap((path+"hp_y_body.png").c_str());
	if(!Gui.hp_y_body){logger::Write("hp_y_body.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_y_end=al_load_bitmap((path+"hp_y_end.png").c_str());
	if(!Gui.hp_y_end){logger::Write("hp_y_end.png==NULL",logger::level::fatal_error);return false;};
	
	Gui.hp_y_start=al_load_bitmap((path+"hp_y_start.png").c_str());
	if(!Gui.hp_y_start){logger::Write("hp_y_start.png==NULL",logger::level::fatal_error);return false;};

	Gui.minihp_g=al_load_bitmap((path+"minihp_g.png").c_str());
	if(!Gui.minihp_g){logger::Write("minihp_g.png==NULL",logger::level::fatal_error);return false;};

	Gui.minihp_r=al_load_bitmap((path+"minihp_r.png").c_str());
	if(!Gui.minihp_r){logger::Write("minihp_r.png==NULL",logger::level::fatal_error);return false;};

	Gui.minihp_y=al_load_bitmap((path+"minihp_y.png").c_str());
	if(!Gui.minihp_y){logger::Write("minihp_y.png==NULL",logger::level::fatal_error);return false;};

	Gui.nametag_body=al_load_bitmap((path+"nametag_body.png").c_str());
	if(!Gui.nametag_body){logger::Write("nametag_body.png==NULL",logger::level::fatal_error);return false;};


	Gui.nametag_end=al_load_bitmap((path+"nametag_end.png").c_str());
	if(!Gui.nametag_end){logger::Write("nametag_end.png==NULL",logger::level::fatal_error);return false;};

	Gui.nametag_start=al_load_bitmap((path+"nametag_start.png").c_str());
	if(!Gui.nametag_start){logger::Write("nametag_start.png==NULL",logger::level::fatal_error);return false;};

	Gui.score=al_load_bitmap((path+"score.png").c_str());
	if(!Gui.score){logger::Write("score.png==NULL",logger::level::fatal_error);return false;};

	Gui.bottom_cd_skill=al_load_bitmap((path+"bottom_cd_skill.png").c_str());
	if(!Gui.bottom_cd_skill){logger::Write("bottom_cd_skill.png==NULL",logger::level::fatal_error);return false;};

	win=al_load_bitmap("data\\win.png");
	if(!win){logger::Write("win.png==NULL",logger::level::fatal_error);return false;};

	lose=al_load_bitmap("data\\lose.png");
	if(!lose){logger::Write("lose.png==NULL",logger::level::fatal_error);return false;};


	return true;	
}

void resources::splashInfo(string text)
{
	al_clear_to_color(al_map_rgb(0,0,0)); 
	al_draw_bitmap(splash,0,0,0); 
	al_draw_text(Fonts.font48, al_map_rgb(255, 255, 255),engine::getInstance().Window.width/2,engine::getInstance().Window.height-100, ALLEGRO_ALIGN_CENTRE, text.c_str());
	al_flip_display();
}

bool resources::LoadResourcesFont()
{
	string path="data/fonts/";
	//font debug/loading
	Fonts.font48 = al_load_font((path+"arial_bold.ttf").c_str(), 48, NULL);
	if(!Fonts.font48){logger::Write("Fonts.font48==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};
	
	Fonts.font12 = al_load_font((path+"arial_bold.ttf").c_str(), 12, NULL);
	if(!Fonts.font12 ){logger::Write("Fonts.font12==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};

	
	//font gui
	Fonts.font25 = al_load_font((path+"arial_bold.ttf").c_str(), 25, NULL);
	if(!Fonts.font25 ){logger::Write("Fonts.font25==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};

	Fonts.font20 = al_load_font((path+"arial_bold.ttf").c_str(), 20, NULL);
	if(!Fonts.font20 ){logger::Write("Fonts.font20==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};

	Fonts.font15 = al_load_font((path+"arial_bold.ttf").c_str(), 15, NULL);
	if(!Fonts.font15 ){logger::Write("Fonts.font15==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};

	Fonts.font16 = al_load_font((path+"arial_bold.ttf").c_str(), 16, NULL);
	if(!Fonts.font16){logger::Write("Fonts.font16==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};

	Fonts.font11 = al_load_font((path+"arial_bold.ttf").c_str(), 11, NULL);
	if(!Fonts.font11 ){logger::Write("Fonts.font11==NULL - arial_bold.ttf",logger::level::fatal_error);return false;};


	return true;

}
bool resources::LoadResourcesHeroes()
{
	string path="data/heroes/";

	for(int i=0;i<game_info.game_players.size();i++)
	{
		bool find=false;
		for(int j=0;j<heroes.size();j++)
		{
			if(heroes[j]->name==game_info.game_players[i].char_name)
			{
				find=true;
				break;
			}
		}
		if(find==false)
		{
			Hero *hero=new Hero();
			if(hero->load(path+game_info.game_players[i].char_name)==false)
			{
				logger::Write(path+game_info.game_players[i].char_name+"  ==NULL",logger::level::fatal_error);
				return false;
			};
			heroes.push_back(hero);
		}
	}
	return true;
}

bool resources::LoadResourcesMaps()
{
	string path="data/maps/";

	if(map.load(path+game_info.name_map)==0) {logger::Write(path+game_info.name_map+" ==NULL",logger::level::fatal_error);return false;};
	
	return true;
}

bool resources::LoadResourcesShots()
{
	string path="data/shot/";

	for(int i=0;i<heroes.size();i++)
	{
		for(int j=0;j<heroes[i]->related_shots.size();j++)
		{
			bool znal=false;
			for(int k=0;k<shots.size();k++)
			{
				if(shots[k]->id==heroes[i]->related_shots[j]) znal=true;
			}

			if(znal==false)
			{
				ostringstream ss;
				ss<<heroes[i]->related_shots[j];
				Shot *shot=new Shot();
				if(shot->load(path+ss.str())==false){logger::Write(path+ss.str()+" ==NULL",logger::level::fatal_error);return false;};
				shot->id=heroes[i]->related_shots[j];
				shots.push_back(shot);
			}
		}
	}
	return true;
}
bool resources::LoadResourcesBuffs()
{
	string path="data/buffs/";

	for(int i=0;i<heroes.size();i++)
	{
		for(int j=0;j<heroes[i]->related_buffs.size();j++)
		{
			bool znal=false;
			for(int k=0;k<buffs.size();k++)
			{
				if(buffs[k]->id==heroes[i]->related_buffs[j]) znal=true;
			}

			if(znal==false)
			{
				ostringstream ss;
				ss<<heroes[i]->related_buffs[j];
				Buff *buff=new Buff();
				if(buff->load(path+ss.str())==false){logger::Write(path+ss.str()+" ==NULL",logger::level::fatal_error);return false;};
				buff->id=heroes[i]->related_buffs[j];
				buffs.push_back(buff);
			}
		}
	}
	return true;
}