#include "gui.h"
#include "engine.h"
#include "../resources/resources.h"
#include "../logger.h"
gui::gui()
{
}

gui& gui::getInstance()
{
          //Inicjalizacja statycznego obiektu.
          //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
          //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
          //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
          static gui instance;
          return instance;
}

void gui::DrawGUI()
{
	DrawHeroInfo();
	DrawBuffs();
	DrawTop();
	DrawBottom();
	
	NavigationDraw();
}

void gui::DrawHeroInfo()
{
	logger::Write("gui::DrawHeroInfo()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();

	for(int i=0;i<eng.heroes_simulation.size();i++)
	{

		if(eng.heroes_simulation[i]->dead==false)
		{
			ostringstream ss;
			ss <<res.game_info.game_players[i].login;
			int x=0,y=0;
			
			x=eng.heroes_simulation[i]->hero_x_relative;
			y=eng.heroes_simulation[i]->hero_y_relative-30;


			//tlo
			int dl= al_get_text_width(res.Fonts.font12, ss.str().c_str())+10;
			if(dl<50) dl=50;
			al_draw_bitmap(res.Gui.nametag_start,x,y,0);
			for(int j=2;j<dl-2;j++)
			{
				al_draw_bitmap(res.Gui.nametag_body,x+j,y,0);
			}
			al_draw_bitmap(res.Gui.nametag_end,x+dl-2,y,0);

			if(res.game_info.game_players[res.game_info.me].team==res.game_info.game_players[i].team)
			{
				al_draw_text(res.Fonts.font12, al_map_rgb(142,180,38),x+(dl/2)-al_get_text_width(res.Fonts.font12, ss.str().c_str())/2, y+4, ALLEGRO_ALIGN_LEFT,ss.str().c_str());
			}
			else
			{
				al_draw_text(res.Fonts.font12, al_map_rgb(180,60,60),x+(dl/2)-al_get_text_width(res.Fonts.font12, ss.str().c_str())/2, y+4, ALLEGRO_ALIGN_LEFT,ss.str().c_str());

			}	

			//draw health bar
			float width_bar_max=dl-4;
			float max_hp=res.heroes[eng.heroes_simulation[i]->id_resource]->hp;
			float now_hp=eng.heroes_simulation[i]->hp_now;
			float width_bar=width_bar_max/max_hp*now_hp;
			float procent=now_hp/max_hp*100;

			if(procent<=30)
			{
				for(int j=0;j<width_bar;j++)
				{
					al_draw_bitmap(res.Gui.minihp_r,x+j+2,y+22,0);
				}
			}
			else if(procent<=70)
			{
				for(int j=0;j<width_bar;j++)
				{
					al_draw_bitmap(res.Gui.minihp_y,x+j+2,y+22,0);
				}
			}
			else if(procent<=100)
			{
				for(int j=0;j<width_bar;j++)
				{
					al_draw_bitmap(res.Gui.minihp_g,x+j+2,y+22,0);
				}
			}
		}
	}

	logger::Write("gui::DrawHeroInfo()-end",logger::level::debug);

}

void gui::DrawTop()
{
	logger::Write("gui::DrawTop()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();
	
	//top score
	al_draw_bitmap(res.Gui.score,(eng.Window.width/2)-(187/2),0,0);
	ostringstream ss;
	ss<<eng.ours_kills;
	al_draw_text(res.Fonts.font20, al_map_rgb(142,180,38),(eng.Window.width/2)-(187/2)+20,15, ALLEGRO_ALIGN_LEFT, ss.str().c_str());
	
	ss.str("");
	ss<<eng.enemy_kills;
	al_draw_text(res.Fonts.font20, al_map_rgb(180,60,60),(eng.Window.width/2)+(187/2)-35,15, ALLEGRO_ALIGN_LEFT, ss.str().c_str());

	//right
	int p=1;
	for(int i=0;i<res.game_info.game_players.size();i++)
	{
		if(res.game_info.game_players[i].team!=res.game_info.game_players[res.game_info.me].team)
		{
			al_draw_bitmap(res.Gui.frame_enemy,(eng.Window.width/2)+(187/2)+(p*15)+(45*(p-1)),(60/2)-(38/2),0);
			if(eng.heroes_simulation[i]->dead==false)
			{
				al_draw_bitmap(res.heroes[eng.heroes_simulation[i]->id_resource]->portrait,(eng.Window.width/2)+(187/2)+(p*15)+(45*(p-1))+2,(60/2)-(38/2)+2,0);
			}
			else
			{
				al_draw_bitmap(res.Gui.avatar_dead,(eng.Window.width/2)+(187/2)+(p*15)+(45*(p-1))+2,(60/2)-(38/2)+2,0);
			}
			p++;
		}
	}

	
	//left
	p=1;
	for(int i=0;i<res.game_info.game_players.size();i++)
	{
		if(res.game_info.game_players[i].team==res.game_info.game_players[res.game_info.me].team)
		{
			al_draw_bitmap(res.Gui.frame_friend,((eng.Window.width/2)-(187/2))-(p*15)-(45*p),(60/2)-(38/2),0);
			if(res.game_info.game_players[i].pid==res.game_info.game_players[res.game_info.me].pid)
			{
				al_draw_bitmap(res.Gui.frame_player,((eng.Window.width/2)-(187/2))-(p*15)-(45*p),(60/2)-(38/2),0);
			}
			if(eng.heroes_simulation[i]->dead==false)
			{
				al_draw_bitmap(res.heroes[eng.heroes_simulation[i]->id_resource]->portrait,((eng.Window.width/2)-(187/2))-(p*15)-(45*p)+2,(60/2)-(38/2)+2,0);
				//health bar

				float width_bar_max=41;
				float max_hp=res.heroes[eng.heroes_simulation[i]->id_resource]->hp;
				float now_hp=eng.heroes_simulation[i]->hp_now;
				float width_bar=width_bar_max/max_hp*now_hp;
				float procent=now_hp/max_hp*100;

				if(procent<=30)
				{
					for(int j=0;j<width_bar;j++)
					{
						al_draw_bitmap(res.Gui.minihp_r,((eng.Window.width/2)-(187/2))-(p*15)-(45*p)+2+j,(60/2)-(38/2)+37,0);
					}
				}
				else if(procent<=70)
				{
					for(int j=0;j<width_bar;j++)
					{
						al_draw_bitmap(res.Gui.minihp_y,((eng.Window.width/2)-(187/2))-(p*15)-(45*p)+2+j,(60/2)-(38/2)+37,0);
					}
				}
				else if(procent<=100)
				{
					for(int j=0;j<width_bar;j++)
					{
						al_draw_bitmap(res.Gui.minihp_g,((eng.Window.width/2)-(187/2))-(p*15)-(45*p)+2+j,(60/2)-(38/2)+37,0);
					}
				}

			}
			else
			{
				al_draw_bitmap(res.Gui.avatar_dead,((eng.Window.width/2)-(187/2))-(p*15)-(45*p)+2,(60/2)-(38/2)+2,0);
			}
			p++;
		}
	}

	
	logger::Write("gui::DrawTop()-end",logger::level::debug);

}

void gui::DrawBottom()
{
	logger::Write("gui::DrawBottom()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();
	//bottom gui
	al_draw_bitmap(res.Gui.bottom_body,(eng.Window.width/2)-(475/2),eng.Window.height-71,0);
	for(int i=0;i<5;i++)
	{
		if(res.heroes[eng.heroes_simulation[res.game_info.me]->id_resource]->skills[i]->AnimationHeroID==eng.heroes_simulation[res.game_info.me]->Animation_intercept.id_animation ||
			res.heroes[eng.heroes_simulation[res.game_info.me]->id_resource]->skills[i]->AnimationHeroID+1==eng.heroes_simulation[res.game_info.me]->Animation_intercept.id_animation)
		{
			if(eng.heroes_simulation[res.game_info.me]->animation_intercept_true==true)
			{
				al_draw_bitmap(res.Gui.bottom_active_skill,(eng.Window.width/2)-(475/2)+94+i*61,eng.Window.height-51,0);
			}
		}

		if(eng.heroes_simulation[res.game_info.me]->cds[i]>0)
		{
			al_draw_tinted_bitmap(res.Gui.bottom_cd_skill,
								al_map_rgba_f(1, 1, 1, 0.5),
								(eng.Window.width/2)-(475/2)+94+i*61+2,
								eng.Window.height-51+2,
								0);
			ostringstream ss;
			ss.precision(1);
			ss<<fixed<<(float)eng.heroes_simulation[res.game_info.me]->cds[i]/1000;
			al_draw_text(res.Fonts.font12, al_map_rgb(0,0,0),(eng.Window.width/2)-(475/2)+94+i*61+15,eng.Window.height-40,ALLEGRO_ALIGN_LEFT,ss.str().c_str());
		}
	}
	//<---- tutaj obrazki skilli
	al_draw_bitmap(res.Gui.bottom_text,(eng.Window.width/2)-(475/2),eng.Window.height-71,0);
	DrawFpsCounter();
	DrawPing();

	//portrait2
	al_draw_bitmap(res.heroes[eng.heroes_simulation[res.game_info.me]->id_resource]->portrait2,(eng.Window.width/2)-(475/2)+20,eng.Window.height-55,0);

	//healthbar	
	float width_bar_max=462;
	float max_hp=res.heroes[eng.heroes_simulation[res.game_info.me]->id_resource]->hp;
	float now_hp=eng.heroes_simulation[res.game_info.me]->hp_now;
	float width_bar=width_bar_max/max_hp*now_hp;
	float procent=now_hp/max_hp*100;
	if(width_bar!=0)
	{
		if(procent<=30)
		{
			al_draw_bitmap(res.Gui.hp_r_start,(eng.Window.width/2)-(475/2)+5,eng.Window.height-67,0);
			for(int i=0;i<width_bar;i++)
			{
				al_draw_bitmap(res.Gui.hp_r_body,(eng.Window.width/2)-(475/2)+7+i,eng.Window.height-67,0);
			}
			al_draw_bitmap(res.Gui.hp_r_end,(eng.Window.width/2)-(475/2)+7+width_bar,eng.Window.height-67,0);
		}
		else if(procent<=70)
		{
			al_draw_bitmap(res.Gui.hp_y_start,(eng.Window.width/2)-(475/2)+5,eng.Window.height-67,0);
			for(int i=0;i<width_bar;i++)
			{
				al_draw_bitmap(res.Gui.hp_y_body,(eng.Window.width/2)-(475/2)+7+i,eng.Window.height-67,0);
			}
			al_draw_bitmap(res.Gui.hp_y_end,(eng.Window.width/2)-(475/2)+7+width_bar,eng.Window.height-67,0);
		}
		else if(procent<=100)
		{
			al_draw_bitmap(res.Gui.hp_g_start,(eng.Window.width/2)-(475/2)+5,eng.Window.height-67,0);
			for(int i=0;i<width_bar;i++)
			{
				al_draw_bitmap(res.Gui.hp_g_body,(eng.Window.width/2)-(475/2)+7+i,eng.Window.height-67,0);
			}
			al_draw_bitmap(res.Gui.hp_g_end,(eng.Window.width/2)-(475/2)+7+width_bar,eng.Window.height-67,0);
		}
	}

	ostringstream ss;
	ss<<eng.heroes_simulation[res.game_info.me]->hp_now<<" / "<<res.heroes[eng.heroes_simulation[res.game_info.me]->id_resource]->hp;
	al_draw_text(res.Fonts.font16, al_map_rgb(255, 255, 255),(eng.Window.width/2)-(8*ss.str().length()/2),eng.Window.height-70, ALLEGRO_ALIGN_LEFT, ss.str().c_str());

	logger::Write("gui::DrawBottom()-end",logger::level::debug);

}
void gui::DrawPing()
{
	logger::Write("gui::DrawPing()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();

	ostringstream ss;
	ss<<"PING "<<eng.old_ping<<" ms";
	al_draw_text(res.Fonts.font11, al_map_rgb(95,162,198),(eng.Window.width/2)+0.65*(475/2),eng.Window.height-45, ALLEGRO_ALIGN_LEFT, ss.str().c_str());

	logger::Write("gui::DrawPing()-end",logger::level::debug);

}
void gui::DrawFpsCounter()
{
	logger::Write("gui::DrawFpsCounter()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();

	double game_time = al_get_time();
    if(game_time - FPS_counter.old_time >= 1.0) 
	{
		  FPS_counter.fps = FPS_counter.frames_done / (game_time - FPS_counter.old_time);
		  FPS_counter.frames_done = 0;
		  FPS_counter.old_time = game_time;
    }
    FPS_counter.frames_done++;
	
	ostringstream ss;
	ss.precision(0);
	ss << "FPS "<<fixed<<FPS_counter.fps;
	string fps_string = ss.str();

	al_draw_text(res.Fonts.font11, al_map_rgb(95,162,198),(eng.Window.width/2)+0.67*(475/2),eng.Window.height-25, ALLEGRO_ALIGN_LEFT, ss.str().c_str());
	
	logger::Write("gui::DrawFpsCounter()-end",logger::level::debug);

}

void gui::NavigationDraw()
{
	logger::Write("gui::NavigationDraw()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();
	
	for(int i=0;i<res.game_info.game_players.size();i++)
	{

		if(eng.heroes_simulation[i]->dead==false)
		{
			if(res.game_info.me==i) continue;

			if(res.game_info.game_players[res.game_info.me].team==res.game_info.game_players[i].team)
			{
			}
			else
			{
				continue;
			}

			if(eng.heroes_simulation[i]->hero_x>eng.Map_fragment.x+eng.Window.width || 
				eng.heroes_simulation[i]->hero_x<eng.Map_fragment.x || 
				eng.heroes_simulation[i]->hero_y>eng.Map_fragment.y+eng.Window.height ||
				eng.heroes_simulation[i]->hero_y<eng.Map_fragment.y)
			{
				int A[2];
				int B[2];
				vector<int> result;
				A[0]=eng.heroes_simulation[res.game_info.me]->hero_x_relative;
				A[1]=eng.heroes_simulation[res.game_info.me]->hero_y_relative;
				B[0]=eng.heroes_simulation[i]->hero_x_relative;
				B[1]=eng.heroes_simulation[i]->hero_y_relative;
				result=punkt_przeciecia(A[0],A[1],B[0],B[1],eng.Window.width,eng.Window.height);
				
				al_draw_bitmap(res.Gui.ball_friend,result[0]-al_get_bitmap_width(res.Gui.ball_friend)/2,result[1]-al_get_bitmap_height(res.Gui.ball_friend)/2,0);
			}
		}
	}

	logger::Write("gui::NavigationDraw()-end",logger::level::debug);

}

vector<int> gui::punkt_przeciecia(int A_x,int A_y,int B_x,int B_y,int maxX, int maxY)
{
	vector<int> result;
	int x=B_x-A_x;
	int y=B_y-A_y;
	if(x==0)
	{
		if(y<0)
		{
			result.push_back(A_x);
			result.push_back(0);
			return result;
		}
		else
		{
			result.push_back(A_x);
			result.push_back(maxY);
			return result;
		}
	}

	if(y==0)
	{
		if(x<0)
		{
			result.push_back(0);
			result.push_back(A_y);
			return result;
		}
		else
		{
			result.push_back(maxX);
			result.push_back(A_y);
			return result;
		}
	}

	int ppx;
	int ppy;
	if(x<0)
	{
		ppx=0;
	}
	else
	{
		ppx=maxX;
	}

	if(y<0)
	{
		ppy=0;
	}
	else
	{
		ppy=maxY;
	}

	double vcx=ppx-A_x;
	double vcy=vcx*y/x;

	double vdy=ppy-A_y;
	double vdx=vdy*x/y;

	double c=sqrt((vcx*vcx+vcy*vcy));
	double d=sqrt((vdx*vdx+vdy*vdy));

	vector <int> krotszy_wektor;
	if(d<c)
	{
		krotszy_wektor.push_back(vdx);
		krotszy_wektor.push_back(vdy);
	}
	else
	{
		krotszy_wektor.push_back(vcx);
		krotszy_wektor.push_back(vcy);
	}

	result.push_back((A_x+krotszy_wektor[0]));
	result.push_back((A_y+krotszy_wektor[1]));

	return result;

}

void gui::DrawBuffs()
{
	
	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();

	for(int i=0;i<res.game_info.game_players.size();i++)
	{
		if(eng.heroes_simulation[i]->dead==false)
		{
			int przesuniecie=0;
			for(int j=0;j<eng.buffs_simulation.size();j++)
			{
				if(eng.buffs_simulation[j]->PID==res.game_info.game_players[i].pid)
				{
					int x=eng.heroes_simulation[i]->hero_x_relative+(przesuniecie*22);
					int y=eng.heroes_simulation[i]->hero_y_relative-51;
					al_draw_bitmap(res.buffs[eng.buffs_simulation[j]->ID_resource]->picture,x,y,0);
					if(eng.buffs_simulation[j]->stacks>1)
					{
						stringstream ss;
						ss<<(float)eng.buffs_simulation[j]->stacks;
						al_draw_text(res.Fonts.font20, al_map_rgb(255,0,0),x+5, y, ALLEGRO_ALIGN_LEFT,ss.str().c_str());
					}
					przesuniecie++;
				}
			}
		}
	}
}