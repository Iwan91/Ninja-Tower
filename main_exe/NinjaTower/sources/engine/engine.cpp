#include "engine.h"
#include "../resources/resources.h"
#include "../resources/Hero.h"
#include "input.h"
#include "../game.h"
#include "../sockets/communication.h"
#include "sound.h"
#include "gui.h"
engine::engine()
{
}

engine& engine::getInstance()
{
          //Inicjalizacja statycznego obiektu.
          //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
          //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
          //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
          static engine instance;
          return instance;
}

void engine::InitEngine()
{
	logger::Write("engine::InitEngine()-start",logger::level::debug);

	al_init_font_addon();
	al_init_ttf_addon();
	al_init_image_addon();
	al_init_primitives_addon();
	al_init_acodec_addon();
	al_init();
	al_install_mouse();
	al_install_keyboard();
	al_install_audio();

	al_reserve_samples(1000);//max ilosc odtwarzanych naraz sampli

	Window.width=1280;
	Window.height=720;
	FPS=40;

	//al_set_new_display_flags(ALLEGRO_FULLSCREEN);
	display = al_create_display(Window.width, Window.height);
	event_queue = al_create_event_queue();
	timer = al_create_timer(1.0 / FPS);

	al_register_event_source(event_queue, al_get_display_event_source(display));
	al_register_event_source(event_queue, al_get_timer_event_source(timer));
	al_register_event_source(event_queue, al_get_mouse_event_source());
	al_register_event_source(event_queue, al_get_keyboard_event_source());

	al_start_timer(timer);

	logger::Write("engine::InitEngine()-stop",logger::level::debug);

}

void engine::PrepareStage()
{
	logger::Write("engine::PrepareStage()-start",logger::level::debug);

	resources &res = resources::getInstance();

	for(int i=0;i<res.game_info.game_players.size();i++)
	{
		hero_simulation *hero= new hero_simulation();
		//find id resource
		for(int j=0;j<res.heroes.size();j++)
		{
			if(res.game_info.game_players[i].char_name==res.heroes[j]->name)
			{
				hero->id_resource=j;
				hero->hero_x=res.map.spawnTeams[res.game_info.game_players[i].team].x;
				hero->hero_y=res.map.spawnTeams[res.game_info.game_players[i].team].y;
				hero->Animation.frame_display=0;
				hero->Animation.frame_count=0;
				hero->Animation.frame_delay=FPS/res.heroes[j]->animations[0]->SpeedOfAnimation;
				hero->Animation.id_animation=0;
				hero->Animation.change_animation=1;
				hero->dead=false;
				hero->animation_intercept_true=false;
				hero->dx=0;
				hero->dy=0;
				hero->hp_now=res.heroes[j]->hp;
				for(int k=0;k<5;k++)
				{
					hero->cds.push_back(0);
				}
				heroes_simulation.push_back(hero);
				break;
			}
		}	
	}

	Map_fragment.x=heroes_simulation[res.game_info.me]->hero_x-(Window.width/2);
	Map_fragment.y=heroes_simulation[res.game_info.me]->hero_y-((Window.height)/2);

	logger::Write("engine::PrepareStage()-end",logger::level::debug);

}
void engine::MainLoopGame()
{
	logger::Write("engine::MainLoopGame()-start",logger::level::debug);

	bool quit=false;
	bool redraw=false;

	while(quit==false)
	{
		ALLEGRO_EVENT ev;
		al_wait_for_event(event_queue, &ev);
		if(ev.type == ALLEGRO_EVENT_TIMER) 
		{
			redraw = true;
		}
		
		if(ev.type == ALLEGRO_EVENT_DISPLAY_CLOSE) 
		{
			quit=true;
		}

		if(ev.type==ALLEGRO_EVENT_KEY_DOWN)
		{
			input::getInstance().keyboard.keydown(&ev.keyboard);
		}

		if(ev.type==ALLEGRO_EVENT_KEY_UP)
		{
			input::getInstance().keyboard.keyup(&ev.keyboard);
		}

		if(ev.type == ALLEGRO_EVENT_MOUSE_AXES || ev.type == ALLEGRO_EVENT_MOUSE_ENTER_DISPLAY) 
		{
			input::getInstance().mouse.x_relative=ev.mouse.x;
			input::getInstance().mouse.y_relative=ev.mouse.y;
		}
		
		if(ev.type == ALLEGRO_EVENT_MOUSE_BUTTON_UP)
		{
			input::getInstance().mouse.keyup(&ev.mouse);
		}

		if(ev.type == ALLEGRO_EVENT_MOUSE_BUTTON_DOWN)
		{
			input::getInstance().mouse.keydown(&ev.mouse);
		}

		if(redraw==true && al_is_event_queue_empty(event_queue)) 
		{
			redraw = false; 
			NetworkTCP();
			NetworkUDP();
			al_clear_to_color(al_map_rgb(0,0,0));
			DrawMap();
			DrawHeroes();
			DrawShots();
			gui::getInstance().DrawGUI();
			sound::getInstance().PlaySounds();

			if(game::getInstance().debug==1) DrawDebugInfo();

			UpdateHeroFrames();
			UpdateShotsFrames();
			
			input::getInstance().keyboard.keyupdate();
			input::getInstance().keyboard.keycheck();
			input::getInstance().SendActionKey();
			CalculateCDs();
			SendPing();
			al_flip_display();
		}
	}

}

void engine::SendPing()
{
	logger::Write("engine::SendPing()-start",logger::level::debug);

	if(send_ping>=1000)
	{
		send_ping=0;
		time_ping=0;
		char ping_c='\x00';
		string ping_s;
		ping_s=ping_c;
		communication::getInstance().SendUDP(ping_s);
	}
	else
	{
		send_ping+=1000/FPS;
	}
	time_ping+=1000/FPS;

	logger::Write("engine::SendPing()-end",logger::level::debug);
}

#define stala_swiata (1.0)
//25/33.3 przy 30 FPS
void engine::NetworkTCP()
{
	logger::Write("engine::NetworkTCP()-start",logger::level::debug);

	#pragma pack(1)
	struct pakiet5 
	{
		unsigned short pid;
		unsigned short HP;
	};
	#pragma pack(1)
	struct pakiet2 
	{
		unsigned short SID;
		unsigned short id_shot;
		unsigned short x;
		unsigned short y;
		float dx;
		float dy;
		unsigned char id_animation;
	};
	#pragma pack(1)
	struct pakiet4podpakiet6
	{
		unsigned short PID;
		unsigned short skillID;
	};
	#pragma pack(1)
	struct pakiet4podpakiet7
	{
		unsigned short PID;
		unsigned short BID;
		unsigned char stacks;
		unsigned short expires;
	};

	resources &res = resources::getInstance();
	string msg=communication::getInstance().ReceiveTCP();
	if(msg!="")
	{
		unsigned char bajt=*((unsigned char*)msg.c_str());
		msg.erase(0,1);
		if(bajt==4)
		{
			unsigned int *iteration=(unsigned int*)msg.c_str();
			msg.erase(0,4);
			while(msg!="")
			{
				if(msg[0]==0)//gracz umar³
				{
					msg.erase(0,1);
					unsigned short *pid=(unsigned short*)msg.c_str();

					for(int i=0;i<res.game_info.game_players.size();i++)
					{
						if(res.game_info.game_players[i].pid==*pid)
						{
							heroes_simulation[i]->dead=true;
							heroes_simulation[i]->dx=0;
							heroes_simulation[i]->dy=0;
							if(res.game_info.game_players[i].team==res.game_info.game_players[res.game_info.me].team)
							{
								enemy_kills++;
							}
							else
							{
								ours_kills++;
							}

							break;
						}
					}
					msg.erase(0,2);
				}

				if(msg[0]==1)// gracz odzyl
				{
					msg.erase(0,1);
					unsigned short *pid=(unsigned short*)msg.c_str();

					for(int i=0;i<res.game_info.game_players.size();i++)
					{
						if(res.game_info.game_players[i].pid==*pid)
						{
							heroes_simulation[i]->dead=false;
							break;
						}
					}
					msg.erase(0,2);
				}

				if(msg[0]==2)// utworzono strzal tracked
				{
					msg.erase(0,1);
					pakiet2 *p2=(pakiet2*)msg.c_str();
					shot_simulation *shot=new shot_simulation();
					shot->sid=p2->SID;
					for(int i=0;i<res.shots.size();i++)
					{
						if(res.shots[i]->id==p2->id_shot) shot->id_resource=i;
					}
					shot->shot_x=p2->x;
					shot->shot_y=p2->y;
					shot->dx=p2->dx;
					shot->dy=p2->dy;
					shot->Animation.frame_display=0;
					shot->Animation.frame_count=0;
					shot->Animation.frame_delay=FPS/res.shots[shot->id_resource]->animations[p2->id_animation]->SpeedOfAnimation;
					shot->Animation.change_animation=1;
					shot->Animation.id_animation=p2->id_animation;
					shot->tracked=1;
					shots_simulation.push_back(shot);
					msg.erase(0,17);
				}

				if(msg[0]==3)//strzal zniszczony
				{
					msg.erase(0,1);
					unsigned short *pid=(unsigned short*)msg.c_str();
					for(int i=0;i<shots_simulation.size();i++)
					{
						if(*pid==shots_simulation[i]->sid)
						{
							if(res.shots[shots_simulation[i]->id_resource]->has_death_animation==1)
							{
								int count=res.shots[shots_simulation[i]->id_resource]->animations.size();
								shots_simulation[i]->Animation.id_animation+=(count/2);
								shots_simulation[i]->Animation.change_animation=true;
							}
							else
							{
								shots_simulation.erase(shots_simulation.begin()+i);
							}
							break;
						}
					}
					msg.erase(0,2);
				}

				if(msg[0]==4)//utworono strzal non-tracked
				{
					msg.erase(0,1);
					msg.erase(0,17);
				}

				if(msg[0]==5) //Graczowi zmieni³o siê HP na skutek obra¿eñ lub heala
				{
					msg.erase(0,1);
					pakiet5 *p5=(pakiet5*)msg.c_str();
					for(int i=0;i<res.game_info.game_players.size();i++)
					{
						if(res.game_info.game_players[i].pid==p5->pid)
						{
							heroes_simulation[i]->hp_now=p5->HP;
							break;
						}
					}
					msg.erase(0,4);
				}

				if(msg[0]==6) //Gracz u¿y³ skilla
				{
					msg.erase(0,1);
					pakiet4podpakiet6 *p6=(pakiet4podpakiet6*)msg.c_str();
					for(int i=0;i<res.game_info.game_players.size();i++)
					{
						if(res.game_info.game_players[i].pid==p6->PID)
						{
							for(int j=0;j<res.heroes[heroes_simulation[i]->id_resource]->skills.size();j++)
							{
								if(res.heroes[heroes_simulation[i]->id_resource]->skills[j]->skillID==p6->skillID)
								{
									heroes_simulation[i]->cds[j]=res.heroes[heroes_simulation[i]->id_resource]->skills[j]->cooldown*1000;
									if(res.heroes[heroes_simulation[i]->id_resource]->skills[j]->AnimationHeroID>-1)
									{
										heroes_simulation[i]->animation_intercept_true=true;
										heroes_simulation[i]->Animation_intercept.frame_count=0;
										heroes_simulation[i]->Animation_intercept.frame_display=0;
										if(heroes_simulation[i]->Animation.id_animation%2)
										{
											heroes_simulation[i]->Animation_intercept.id_animation=res.heroes[heroes_simulation[i]->id_resource]->skills[j]->AnimationHeroID+1;
											heroes_simulation[i]->Animation_intercept.frame_delay=FPS/res.heroes[heroes_simulation[i]->id_resource]->animations[res.heroes[heroes_simulation[i]->id_resource]->skills[j]->AnimationHeroID+1]->SpeedOfAnimation;
										}
										else
										{
											heroes_simulation[i]->Animation_intercept.id_animation=res.heroes[heroes_simulation[i]->id_resource]->skills[j]->AnimationHeroID;
											heroes_simulation[i]->Animation_intercept.frame_delay=FPS/res.heroes[heroes_simulation[i]->id_resource]->animations[res.heroes[heroes_simulation[i]->id_resource]->skills[j]->AnimationHeroID]->SpeedOfAnimation;
										}
									}

								}
							}
						}
					}
					msg.erase(0,4);
				}

				if(msg[0]==7) //Zmiana stanu buffa na graczu 
				{
					msg.erase(0,1);
					pakiet4podpakiet7 *p7=(pakiet4podpakiet7*)msg.c_str();

					if(p7->stacks==0 || p7->expires==0)
					{
						for(int i=0;i<buffs_simulation.size();i++)
						{
							if(p7->PID==buffs_simulation[i]->PID && p7->BID==buffs_simulation[i]->BID)
							{
								buffs_simulation.erase(buffs_simulation.begin()+i);
								break;
							}
						}
					}
					else
					{
						bool znal=false;
						for(int i=0;i<buffs_simulation.size();i++)
						{
							if(p7->PID==buffs_simulation[i]->PID && p7->BID==buffs_simulation[i]->BID)
							{
								buffs_simulation[i]->expires=p7->expires;
								buffs_simulation[i]->stacks=p7->stacks;
								znal=true;
								break;
							}
						}

						if(znal==false)
						{
							buff_simulation *buff=new buff_simulation();
							buff->PID=p7->PID;
							buff->BID=p7->BID;
							buff->expires=p7->expires;
							buff->stacks=p7->stacks;

							for(int i=0;i<res.buffs.size();i++)
							{
								if(res.buffs[i]->id==buff->BID) buff->ID_resource=i;
							}
							buffs_simulation.push_back(buff);
						}
					}

					
					msg.erase(0,7);
				}

			}
		}

		if(bajt==6)
		{
			if(msg[0]==res.game_info.game_players[res.game_info.me].team)
			{
				al_draw_bitmap(res.win,(Window.width/2)-(465/2),(Window.height/2)-(465/2),0);
			}
			else
			{
				al_draw_bitmap(res.lose,(Window.width/2)-(465/2),(Window.height/2)-(465/2),0);
			}

			al_flip_display();

			al_rest(5);
			exit(0);

			msg.erase(0,4);
		}

		if(bajt==7)
		{
			unsigned char *team1=(unsigned char*)msg[0];
			unsigned char *team2=(unsigned char*)msg[1];
			if(res.game_info.game_players[res.game_info.me].team==1)
			{
				ours_kills=(int)team2;
				enemy_kills=(int)team1;
			}
			else
			{
				ours_kills=(int)team1;
				enemy_kills=(int)team2;
			}

			msg.erase(0,2);
		}

	}

	logger::Write("engine::NetworkTCP()-end",logger::level::debug);

}
void engine::NetworkUDP()
{
	logger::Write("engine::NetworkUDP()-start",logger::level::debug);

	resources &res = resources::getInstance();
	
	//udp
	#pragma pack(1)
	struct naglowekUDP
	{
		unsigned char generation;
		unsigned long iteration;
	};

	#pragma pack(1)
	struct pakietUDP {
		char k;
		unsigned short type;
		unsigned short x;
		unsigned short y;
		float dx;
		float dy;
	};
	
	for(int i=0;i<heroes_simulation.size();i++)
	{
		stringstream ss;
		ss<<" pid_hero: "<<res.game_info.game_players[i].pid
		<<" ~~client_data2: "<<"iteration_client:"<<iteration_client<<" x="<<heroes_simulation[i]->hero_x<<" y="<<heroes_simulation[i]->hero_y<<" dx="<<heroes_simulation[i]->dx<<" dy="<<heroes_simulation[i]->dy<<" ~~";
		logger::Write(ss.str(),logger::level::debug);

		heroes_simulation[i]->hero_x+=heroes_simulation[i]->dx;
		heroes_simulation[i]->hero_y+=heroes_simulation[i]->dy;
	}

	for(int i=0;i<shots_simulation.size();i++)
	{
		shots_simulation[i]->shot_x+=shots_simulation[i]->dx;
		shots_simulation[i]->shot_y+=shots_simulation[i]->dy;
	}
		
	iteration_client++;

	string msg=communication::getInstance().ReceiveUDP();
	if(msg!="")
	{
		naglowekUDP *n=(naglowekUDP*)msg.c_str();
			
		stringstream ss;
		ss<<n->generation<<" "<<n->iteration;
		logger::Write("Naglowek UDP server: "+ss.str(),logger::level::info);
			
		if(n->generation==1)
		{
			old_ping=time_ping;
			return;
		}

		for(int i=0;i<heroes_simulation.size();i++)
		{
			heroes_simulation[i]->dx=heroes_simulation[i]->dx;
			heroes_simulation[i]->dy=heroes_simulation[i]->dy;
		}
		for(int i=0;i<shots_simulation.size();i++)
		{
			shots_simulation[i]->dx=shots_simulation[i]->dx;
			shots_simulation[i]->dy=shots_simulation[i]->dy;
		}

		if(n->iteration>iteration_udp)
		{
			iteration_udp=n->iteration;
			if(n->generation==0)
			{
				msg.erase(0,5);
				while(msg!="")
				{
					pakietUDP *p=(pakietUDP*)msg.c_str();
					
					int aktor_0_shoot_1 = ((unsigned char)(p->k)) >> 7;
					int id_animacji = (p->k & 127)& 0xBF;
					int down_up= (p->k >> 6) & 1;

					stringstream ss;
					ss<<id_animacji<<" "<<aktor_0_shoot_1<<" "<<p->k<<" "<<p->x<<" "<<p->y<<" "<<p->dx<<" "<<p->dy;
					logger::Write("UDP server: "+ss.str(),logger::level::info);
					
					if(aktor_0_shoot_1==0)
					{
						int id=-1;
						for(int i=0;i<res.game_info.game_players.size();i++)
						{
							if(res.game_info.game_players[i].pid==p->type) id=i;
						}

						stringstream ss;
						ss<<" pid_hero: "<<res.game_info.game_players[id].pid
						<<" ~~client_data: "<<"iteration_client:"<<iteration_client<<" x="<<heroes_simulation[id]->hero_x<<" y="<<heroes_simulation[id]->hero_y<<" dx="<<heroes_simulation[id]->dx<<" dy="<<heroes_simulation[id]->dy<<" ~~"
						<<" !!server_data: "<<"iteration_server: "<<iteration_udp<<" x="<<p->x<<" y="<<p->y<<" dx="<<p->dx<<" dy="<<p->dy<<" !!";
						logger::Write(ss.str(),logger::level::debug);

						ss.str("");
						if(heroes_simulation[id]->hero_x!=p->x)
						{
							ss<<"ROZNICA x="<<heroes_simulation[id]->hero_x-p->x;
							logger::Write(ss.str(),logger::level::debug);
						}

						iteration_client=iteration_udp;

						if(down_up==0)
						{
							heroes_simulation[id]->down_up=0;
						}
						else
						{
							heroes_simulation[id]->down_up=2;
						}
						heroes_simulation[id]->hero_x=p->x;
						heroes_simulation[id]->hero_y=p->y;
						heroes_simulation[id]->dx=p->dx/stala_swiata;
						heroes_simulation[id]->dy=p->dy/stala_swiata;

						if(heroes_simulation[id]->Animation.id_animation!=id_animacji)
						{
							heroes_simulation[id]->Animation.change_animation=1;
							heroes_simulation[id]->Animation.id_animation=id_animacji;
						}
					}
					else
					{
						int id=-1;
						for(int i=0;i<shots_simulation.size();i++)
						{
							if(shots_simulation[i]->sid==p->type) id=i;
						}
						if(id>-1)
						{
							shots_simulation[id]->shot_x=p->x;
							shots_simulation[id]->shot_y=p->y;
							shots_simulation[id]->dx=p->dx/stala_swiata;
							shots_simulation[id]->dy=p->dy/stala_swiata;
							if(shots_simulation[id]->Animation.id_animation!=id_animacji)
							{
								shots_simulation[id]->Animation.change_animation=1;
								shots_simulation[id]->Animation.id_animation=id_animacji;
							}
						}
					}
					msg.erase(0,15);

				}
			}
		}
	}
    
	logger::Write("engine::NetworkUDP()-end",logger::level::debug);

}

void engine::DrawMap()
{
	logger::Write("engine::DrawMap()-start",logger::level::debug);

	resources &res = resources::getInstance();

	Map_fragment.x+=(heroes_simulation[res.game_info.me]->hero_x-(Window.width/2)-Map_fragment.x)*0.3;
	if((Map_fragment.x+Window.width)>res.map.Width) Map_fragment.x=res.map.Width-Window.width;
	if(Map_fragment.x<0) Map_fragment.x=0;
	input::getInstance().mouse.x=input::getInstance().mouse.x_relative+Map_fragment.x;

	Map_fragment.y+=(heroes_simulation[res.game_info.me]->hero_y-((Window.height)/2)-Map_fragment.y)*0.3;
	if((Map_fragment.y+Window.height)>res.map.Height) Map_fragment.y=res.map.Height-Window.height;
	if(Map_fragment.y<0) Map_fragment.y=0;
	input::getInstance().mouse.y=input::getInstance().mouse.y_relative+Map_fragment.y;
	
	//narysowanie mapy
    int klocek_w = 512;
    int klocek_h = 512;

	int ilosc_w = ceil((double)Window.width / (double)klocek_w);
	int ilosc_h = ceil((double)Window.height / (double)klocek_h);

	int columns=ceil((double)res.map.Width/(double)klocek_w);
	int rows=ceil((double)res.map.Height/(double)klocek_h);

	int offset_x=abs(Map_fragment.x-(Map_fragment.x/klocek_w)*klocek_w);
	int offset_y=abs(Map_fragment.y-(Map_fragment.y/klocek_h)*klocek_h);

	for(int i=0;i<=ilosc_h;i++)
	{	
		for(int j=0;j<=ilosc_w;j++)
		{
			int x=(Map_fragment.x+j*klocek_w)/klocek_w;
			int y=(Map_fragment.y+i*klocek_h)/klocek_h;
			
			int id_kafla=columns*y+x;
			if(id_kafla<res.map.pictures.size())
			{
				al_draw_bitmap(res.map.pictures[id_kafla],(j*klocek_w)-offset_x,(i*klocek_h)-offset_y,0);
			}
		}
	}

	
	
	logger::Write("engine::DrawMap()-end",logger::level::debug);
}

void engine::DrawHeroes()
 {
	 logger::Write("engine::DrawHeroes()-start",logger::level::debug);

	 //draw Heroes
	 resources &res = resources::getInstance();

	 for(int i=0;i<heroes_simulation.size();i++)
	 {
		heroes_simulation[i]->hero_x_relative=heroes_simulation[i]->hero_x-Map_fragment.x;//-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_x;
		heroes_simulation[i]->hero_y_relative=heroes_simulation[i]->hero_y-Map_fragment.y;//-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_y;
	 }

	 logger::Write("engine::DrawHeroes()- hero_relative_x_y - OK",logger::level::debug);

	 for(int i=0;i<heroes_simulation.size();i++)
	 {
		stringstream ss;
		ss<<"engine::DrawHeroes()- heroes_simulation="<<i<<" -start";
		logger::Write(ss.str().c_str(),logger::level::debug);

		if(heroes_simulation[i]->dead==false)
		{
			Hero *hero_copy=resources::getInstance().heroes[heroes_simulation[i]->id_resource];

			if(heroes_simulation[i]->Animation.change_animation==true)
			{
				ss.str("");
				ss<<"engine::DrawHeroes()- heroes_simulation="<<i<<" ChangeAnimation";
				logger::Write(ss.str().c_str(),logger::level::debug);

				heroes_simulation[i]->Animation.change_animation=false;
				heroes_simulation[i]->Animation.frame_display=0;
				heroes_simulation[i]->Animation.frame_count=0;
				heroes_simulation[i]->Animation.frame_delay=FPS/hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->SpeedOfAnimation;
			}

			
			if(heroes_simulation[i]->animation_intercept_true==true)
			{

				if(heroes_simulation[i]->down_up==2)
				{
					//int w=al_get_bitmap_width(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[0]->picture);
					heroes_simulation[i]->hero_x_relative-=res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation_intercept.id_animation]->synchroPoint_x;

					int h=al_get_bitmap_height(hero_copy->animations[heroes_simulation[i]->Animation_intercept.id_animation]->frames[0]->picture);
					heroes_simulation[i]->hero_y_relative-=h-hero_copy->animations[heroes_simulation[i]->Animation_intercept.id_animation]->synchroPoint_y;
				}
				else
				{
					heroes_simulation[i]->hero_x_relative+=-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation_intercept.id_animation]->synchroPoint_x;

					heroes_simulation[i]->hero_y_relative+=-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation_intercept.id_animation]->synchroPoint_y;
				}

				ss.str("");
				ss<<"engine::DrawHeroes()- heroes_simulation="<<i<<" DrawInterceptAnimation";
				logger::Write(ss.str().c_str(),logger::level::debug);

				al_draw_bitmap(hero_copy->animations[heroes_simulation[i]->Animation_intercept.id_animation]->frames[heroes_simulation[i]->Animation_intercept.frame_display]->picture, 
								heroes_simulation[i]->hero_x_relative,
								heroes_simulation[i]->hero_y_relative,
								heroes_simulation[i]->down_up);		

			}
			else
			{
				/*al_draw_tinted_bitmap(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[heroes_simulation[i]->Animation.frame_display]->picture,
									al_map_rgba_f(1, 1, 1, 0.2),
									heroes_simulation[i]->hero_x_relative,
								heroes_simulation[i]->hero_y_relative,
								heroes_simulation[i]->down_up);*/
				if(heroes_simulation[i]->down_up==2)
				{
					//int w=al_get_bitmap_width(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[0]->picture);
					heroes_simulation[i]->hero_x_relative-=res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_x;

					int h=al_get_bitmap_height(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[0]->picture);
					heroes_simulation[i]->hero_y_relative-=h-hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_y;
				}
				else
				{
					heroes_simulation[i]->hero_x_relative+=-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_x;

					heroes_simulation[i]->hero_y_relative+=-res.heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->synchroPoint_y;
				}


				ss.str("");
				ss<<"engine::DrawHeroes()- heroes_simulation="<<i<<" DrawNormalAnimation";
				logger::Write(ss.str().c_str(),logger::level::debug);

				al_draw_bitmap(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[heroes_simulation[i]->Animation.frame_display]->picture, 
								heroes_simulation[i]->hero_x_relative,
								heroes_simulation[i]->hero_y_relative,
								heroes_simulation[i]->down_up);
			}
				
		}
		ss.str("");
		ss<<"engine::DrawHeroes()- heroes_simulation="<<i<<" -end";
		logger::Write(ss.str().c_str(),logger::level::debug);

	 }
	
	 
	logger::Write("engine::DrawHeroes()-end",logger::level::debug);

 }

void engine::DrawShots()
{
	 logger::Write("engine::DrawShots()-start",logger::level::debug);

	 resources &res = resources::getInstance();

	 for(int i=0;i<shots_simulation.size();i++)
	 {
		shots_simulation[i]->shot_x_relative=shots_simulation[i]->shot_x-Map_fragment.x-res.shots[shots_simulation[i]->id_resource]->animations[shots_simulation[i]->Animation.id_animation]->synchroPoint_x;
		shots_simulation[i]->shot_y_relative=shots_simulation[i]->shot_y-Map_fragment.y-res.shots[shots_simulation[i]->id_resource]->animations[shots_simulation[i]->Animation.id_animation]->synchroPoint_y;
	 }

	 for(int i=0;i<shots_simulation.size();i++)
	 {
		
		Shot *shot_copy=resources::getInstance().shots[shots_simulation[i]->id_resource];

		if(shots_simulation[i]->Animation.change_animation==true)
		{
			shots_simulation[i]->Animation.change_animation=false;
			shots_simulation[i]->Animation.frame_display=0;
			shots_simulation[i]->Animation.frame_count=0;
			shots_simulation[i]->Animation.frame_delay=FPS/res.shots[shots_simulation[i]->id_resource]->animations[shots_simulation[i]->Animation.id_animation]->SpeedOfAnimation;
		}
		
		al_draw_bitmap(shot_copy->animations[shots_simulation[i]->Animation.id_animation]->frames[shots_simulation[i]->Animation.frame_display]->picture, 
						shots_simulation[i]->shot_x_relative,
						shots_simulation[i]->shot_y_relative,
							0);		

		if(shots_simulation[i]->Animation.id_animation>=(res.shots[shots_simulation[i]->id_resource]->animations.size()/2) 
			&& shots_simulation[i]->Animation.frame_display==res.shots[shots_simulation[i]->id_resource]->animations[shots_simulation[i]->Animation.id_animation]->frames.size()-1
			&& res.shots[shots_simulation[i]->id_resource]->has_death_animation==1)
		{
			shots_simulation.erase(shots_simulation.begin()+i);
		}
	 }

	  logger::Write("engine::DrawShots()-end",logger::level::debug);

}

void engine::UpdateHeroFrames()
{
	logger::Write("engine::UpdateHeroFrames()-start",logger::level::debug);

	for(int i=0;i<heroes_simulation.size();i++)
	{
		if(heroes_simulation[i]->animation_intercept_true==true)
		{
			if(++heroes_simulation[i]->Animation_intercept.frame_count >= heroes_simulation[i]->Animation_intercept.frame_delay)
			{
				if(heroes_simulation[i]->Animation_intercept.frame_display < resources::getInstance().heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation_intercept.id_animation]->frames.size()-1)
				{
					heroes_simulation[i]->Animation_intercept.frame_display++;
				}
				else
				{
					heroes_simulation[i]->Animation_intercept.frame_display=0;
					heroes_simulation[i]->animation_intercept_true=false;
				}
				heroes_simulation[i]->Animation_intercept.frame_count=0;
			}
		}
		else
		{
			if(++heroes_simulation[i]->Animation.frame_count >= heroes_simulation[i]->Animation.frame_delay)
			{
				if(heroes_simulation[i]->Animation.frame_display < resources::getInstance().heroes[heroes_simulation[i]->id_resource]->animations[heroes_simulation[i]->Animation.id_animation]->frames.size()-1)
				{
					heroes_simulation[i]->Animation.frame_display++;
				}
				else
				{
					heroes_simulation[i]->Animation.frame_display=0;
				}
				heroes_simulation[i]->Animation.frame_count=0;
			}
		}
	}

	logger::Write("engine::UpdateHeroFrames()-end",logger::level::debug);

}

void engine::UpdateShotsFrames()
{
	logger::Write("engine::UpdateShotsFrames()-start",logger::level::debug);

	for(int i=0;i<shots_simulation.size();i++)
	{
		if(++shots_simulation[i]->Animation.frame_count >= shots_simulation[i]->Animation.frame_delay)
		{
			if(shots_simulation[i]->Animation.frame_display < resources::getInstance().shots[shots_simulation[i]->id_resource]->animations[shots_simulation[i]->Animation.id_animation]->frames.size()-1)
			{
				shots_simulation[i]->Animation.frame_display++;
			}
			else
			{
				shots_simulation[i]->Animation.frame_display=0;
			}
			shots_simulation[i]->Animation.frame_count=0;
		}
	}

	logger::Write("engine::UpdateShotsFrames()-end",logger::level::debug);

}

void engine::DrawDebugInfo()
{
	InnerDebugInfo();
	DrawHitBoxes();
}

void engine::InnerDebugInfo()
{
	logger::Write("engine::InnerDebugInfo()-start",logger::level::debug);

	resources &res = resources::getInstance();

	ostringstream ss;
	ss.precision(2);
	string temp;
	//polozenie mapy
	ss.str("");
	ss.clear();
	ss <<"Map(x,y)=("<<Map_fragment.x<<", "<<Map_fragment.y<<")"<<'\0';
	temp = ss.str();

	al_draw_text(res.Fonts.font12, al_map_rgb(127, 255, 127), 10, 25, ALLEGRO_ALIGN_LEFT,temp.c_str());

	//polozenie myszki
    ss.str("");
	ss.clear();
	ss <<"Mouse(x,y)=("<<input::getInstance().mouse.x<<", "<<input::getInstance().mouse.y<<")"<<" "<<"Mouse_relative(x,y)=("<<input::getInstance().mouse.x_relative<<", "<<input::getInstance().mouse.y_relative<<")"<<'\0';
	al_draw_text(res.Fonts.font12, al_map_rgb(127, 255, 127), 10, 40, ALLEGRO_ALIGN_LEFT,ss.str().c_str());

	//polozenie wszytskich aktorow i ich dx,dy
	int pol_y=55;
	for(int i=0;i<heroes_simulation.size();i++)
	{
		ss.str("");
		ss.clear();
		ss<< fixed <<"Hero["<<i<<"](x,y)=("<<heroes_simulation[i]->hero_x<<", "<<heroes_simulation[i]->hero_y<<")"<<" (dx,dy)=("<<heroes_simulation[i]->dx<<", "<<heroes_simulation[i]->dy<<")"<<" Relative(x,y)=("<<heroes_simulation[i]->hero_x_relative<<", "<<heroes_simulation[i]->hero_y_relative <<") id_animation="<<heroes_simulation[i]->Animation.id_animation<<" frame_display="<<heroes_simulation[i]->Animation.frame_display<<" - "<< res.heroes[heroes_simulation[i]->id_resource]->name<<'\0';
		temp=ss.str();
		//clog<<temp<<endl;
		al_draw_text(res.Fonts.font12, al_map_rgb(127, 255, 127), 10, pol_y, ALLEGRO_ALIGN_LEFT,temp.c_str());
		pol_y=pol_y+15;
	}


	logger::Write("engine::InnerDebugInfo()-end",logger::level::debug);
}


void engine::DrawHitBoxes()
{
	logger::Write("engine::DrawHitBoxes()-start",logger::level::debug);

	ALLEGRO_COLOR color;
	resources &res = resources::getInstance();

	for(int i=0;i<heroes_simulation.size();i++)
	{
		if(heroes_simulation[i]->dead==false)
		{
			Hero *hero_copy=res.heroes[heroes_simulation[i]->id_resource];
			Animation *animation_copy=hero_copy->animations[heroes_simulation[i]->Animation.id_animation];
			color= al_map_rgb(255,0,0);	
			for(int j=0;j<animation_copy->hitboxes.size();j++)
			{
				if(heroes_simulation[i]->down_up==2)
				{

					int h=al_get_bitmap_height(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[0]->picture);
				
					al_draw_rectangle(heroes_simulation[i]->hero_x_relative+animation_copy->hitboxes[j]->x1, 
										heroes_simulation[i]->hero_y_relative+h-animation_copy->hitboxes[j]->y1, 
										heroes_simulation[i]->hero_x_relative+animation_copy->hitboxes[j]->x2, 
										heroes_simulation[i]->hero_y_relative+h-animation_copy->hitboxes[j]->y2,  
										color, 1);
				}
				else
				{		
					al_draw_rectangle(heroes_simulation[i]->hero_x_relative+animation_copy->hitboxes[j]->x1, 
										heroes_simulation[i]->hero_y_relative+animation_copy->hitboxes[j]->y1, 
										heroes_simulation[i]->hero_x_relative+animation_copy->hitboxes[j]->x2, 
										heroes_simulation[i]->hero_y_relative+animation_copy->hitboxes[j]->y2,  
										color, 1);
				}

			}
			color= al_map_rgb(255, 255, 224);
			if(heroes_simulation[i]->down_up==2)
			{
				int h=al_get_bitmap_height(hero_copy->animations[heroes_simulation[i]->Animation.id_animation]->frames[0]->picture);

				al_draw_rectangle(heroes_simulation[i]->hero_x_relative+animation_copy->synchroPoint_x, 
								heroes_simulation[i]->hero_y_relative+h-animation_copy->synchroPoint_y, 
								heroes_simulation[i]->hero_x_relative+animation_copy->synchroPoint_x, 
								heroes_simulation[i]->hero_y_relative+h-animation_copy->synchroPoint_y,  
								color, 3);
			}
			else
			{
				al_draw_rectangle(heroes_simulation[i]->hero_x_relative+animation_copy->synchroPoint_x, 
								heroes_simulation[i]->hero_y_relative+animation_copy->synchroPoint_y, 
								heroes_simulation[i]->hero_x_relative+animation_copy->synchroPoint_x, 
								heroes_simulation[i]->hero_y_relative+animation_copy->synchroPoint_y,  
								color, 3);
			}
		}

	}

	color= al_map_rgb(184,3,255);

	for(int i=0;i<res.map.platforms.size();i++)
	{
		al_draw_rectangle(res.map.platforms[i].x1-Map_fragment.x,
							res.map.platforms[i].y-Map_fragment.y, 
							res.map.platforms[i].x2-Map_fragment.x, 
							res.map.platforms[i].y-Map_fragment.y,  
							color, 2);
	}

	color= al_map_rgb(218,124,32);	
	for(int i=0;i<res.map.obstacles.size();i++)
	{
		al_draw_rectangle(res.map.obstacles[i].x1-Map_fragment.x,
							res.map.obstacles[i].y1-Map_fragment.y, 
							res.map.obstacles[i].x2-Map_fragment.x, 
							res.map.obstacles[i].y2-Map_fragment.y,  
							color, 2);
	}

	logger::Write("engine::DrawHitBoxes()-end",logger::level::debug);

}

void engine::CalculateCDs()
{
	logger::Write("engine::CalculateCDs()-start",logger::level::debug);

	for(int i=0;i<heroes_simulation.size();i++)
	{
		for(int j=0;j<5;j++)
		{
			if(heroes_simulation[i]->cds[j]>=0) heroes_simulation[i]->cds[j]-=1000/FPS;
		}
	}

	logger::Write("engine::CalculateCDs()-end",logger::level::debug);

}