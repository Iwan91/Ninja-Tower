#include "sound.h"
#include "engine.h"
#include "hero_simulation.h"
#include "shot_simulation.h"
#include "../resources/resources.h"
#include "../resources/Hero.h"
#include <Math.h>
#include "../logger.h"
sound::sound()
{
}

sound& sound::getInstance()
{
          //Inicjalizacja statycznego obiektu.
          //Obiekt zostanie utworzony przy pierwszym wywo³aniu tej metody
          //i tylko wtedy nast¹pi inicjalizacja przy pomocy konstruktora.
          //Ka¿de nastêpne wywo³anie jedynie zwróci referencjê tego obiektu.
          static sound instance;
          return instance;
}

void sound::PlaySounds()
{
	logger::Write("sound::PlaySounds()-start",logger::level::debug);

	if(resources::getInstance().map.sound!=NULL && theme==NULL)
	{
		theme=al_create_sample_instance(resources::getInstance().map.sound);
		al_set_sample_instance_playmode(theme, ALLEGRO_PLAYMODE_LOOP);
		al_set_sample_instance_gain(theme,0.5);
		al_attach_sample_instance_to_mixer(theme, al_get_default_mixer());
		al_play_sample_instance(theme);
	}
	
	DestroySounds();
	GenerateList();
	PlayList();

	logger::Write("sound::PlaySounds()-end",logger::level::debug);

}

void sound::GenerateList()
{
	logger::Write("sound::GenerateList()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();

	//wygenerowanie dŸwieku dla graczy
	for(int i=0;i<eng.heroes_simulation.size();i++)
	{
		if(eng.heroes_simulation[i]->dead!=true)
		{
			int id_animation=-1;
			if(eng.heroes_simulation[i]->animation_intercept_true==true)
			{
				id_animation=eng.heroes_simulation[i]->Animation_intercept.id_animation;
			}
			else
			{
				id_animation=eng.heroes_simulation[i]->Animation.id_animation;
			}

			bool znal=false;
			for(int j=0;j<Sound_info_heroes.size();j++)
			{
				if( (Sound_info_heroes[j]->id==res.game_info.game_players[i].pid) && (Sound_info_heroes[j]->id_animation==id_animation) )
				{
					znal=true;
					break;
				}
			}
			

			if(res.heroes[eng.heroes_simulation[i]->id_resource]->animations[id_animation]->sound!=NULL && znal==false)
			{
				if(intersect_rectangles(
				eng.Map_fragment.x,
				eng.Map_fragment.y,
				eng.Map_fragment.x+eng.Window.width,
				eng.Map_fragment.y+eng.Window.height,
				eng.heroes_simulation[i]->hero_x,
				eng.heroes_simulation[i]->hero_y,
				eng.heroes_simulation[i]->hero_x+1,
				eng.heroes_simulation[i]->hero_y+1
				)==true)
				{
					sound_info *info=new sound_info();
					info->id=res.game_info.game_players[i].pid;
					info->id_animation=id_animation;
					info->instance=al_create_sample_instance(res.heroes[eng.heroes_simulation[i]->id_resource]->animations[id_animation]->sound);
					al_set_sample_instance_playmode(info->instance, ALLEGRO_PLAYMODE_ONCE);
					float pan=0;
					float abs_roznica=abs(eng.Map_fragment.x+eng.Window.width/2-eng.heroes_simulation[i]->hero_x);
					pan=abs_roznica*1/(eng.Window.width/2);

					if(eng.Map_fragment.x+eng.Window.width/2-eng.heroes_simulation[i]->hero_x<=0)
					{
						al_set_sample_instance_pan(info->instance,pan);
					}
					else
					{
						al_set_sample_instance_pan(info->instance,-pan);
					}
					al_attach_sample_instance_to_mixer(info->instance, al_get_default_mixer());
					Sound_info_heroes.push_back(info);
				}
			}
		}
	}
	
	//wygenerowanie dŸwieku dla pocisków
	for(int i=0;i<eng.shots_simulation.size();i++)
	{
		bool znal=false;
		for(int j=0;j<Sound_info_shots.size();j++)
		{
			if( (Sound_info_shots[j]->id==eng.shots_simulation[i]->sid) )
			{
				znal=true;
				break;
			}
		}
		
		if(res.shots[eng.shots_simulation[i]->id_resource]->animations[eng.shots_simulation[i]->Animation.id_animation]->sound!=NULL && znal==false)
		{
			if(intersect_rectangles(
			eng.Map_fragment.x,
			eng.Map_fragment.y,
			eng.Map_fragment.x+eng.Window.width,
			eng.Map_fragment.y+eng.Window.height,
			eng.shots_simulation[i]->shot_x,
			eng.shots_simulation[i]->shot_y,
			eng.shots_simulation[i]->shot_x+1,
			eng.shots_simulation[i]->shot_y+1
			)==true)
			{
				sound_info *info=new sound_info();
				info->id=eng.shots_simulation[i]->sid;
				info->id_animation=eng.shots_simulation[i]->Animation.id_animation;
				info->instance=al_create_sample_instance(res.shots[eng.shots_simulation[i]->id_resource]->animations[eng.shots_simulation[i]->Animation.id_animation]->sound);
				al_set_sample_instance_playmode(info->instance, ALLEGRO_PLAYMODE_ONCE);
				float pan=0;
				float abs_roznica=abs(eng.Map_fragment.x+eng.Window.width/2-eng.shots_simulation[i]->shot_x);
				pan=abs_roznica*1/(eng.Window.width/2);

				if(eng.Map_fragment.x+eng.Window.width/2-eng.shots_simulation[i]->shot_x<=0)
				{
					al_set_sample_instance_pan(info->instance,pan);
				}
				else
				{
					al_set_sample_instance_pan(info->instance,-pan);
				}
				al_attach_sample_instance_to_mixer(info->instance, al_get_default_mixer());
				Sound_info_shots.push_back(info);
			}
		}
	}

	logger::Write("sound::GenerateList()-end",logger::level::debug);

}

void sound::PlayList()
{
	logger::Write("sound::PlayList()-start",logger::level::debug);

	//odtworzenie dzwieku dla bohaterow
	for(int i=0;i<Sound_info_heroes.size();i++)
	{
		if(al_get_sample_instance_playing(Sound_info_heroes[i]->instance)!=true)
		{
			al_play_sample_instance(Sound_info_heroes[i]->instance);
		}
	}

	//odwtorzenie dzwieku dla pociskow
	for(int i=0;i<Sound_info_shots.size();i++)
	{
		if(al_get_sample_instance_playing(Sound_info_shots[i]->instance)!=true)
		{
			al_play_sample_instance(Sound_info_shots[i]->instance);
		}
	}

	logger::Write("sound::PlayList()-end",logger::level::debug);

}

void sound::DestroySounds()
{
	logger::Write("sound::DestroySounds()-start",logger::level::debug);

	resources &res = resources::getInstance();
	engine &eng=engine::getInstance();
	bool sprawdz=true;

	//destroy heroes sound
	sprawdz=true;
	while(sprawdz==true)
	{
		for(int i=0;i<Sound_info_heroes.size();i++)
		{
			if(al_get_sample_instance_playing(Sound_info_heroes[i]->instance)!=true)
			{
				DestroyInstance(Sound_info_heroes, i);
				break;
			}
		}
		sprawdz=false;
	}
	

	sprawdz=true;
	while(sprawdz==true)
	{
		for(int i=0;i<Sound_info_heroes.size();i++)
		{
			for(int j=0;j<eng.heroes_simulation.size();j++)
			{
				if(Sound_info_heroes[i]->id==res.game_info.game_players[j].pid)
				{
					if(intersect_rectangles(
					eng.Map_fragment.x,
					eng.Map_fragment.y,
					eng.Map_fragment.x+eng.Window.width,
					eng.Map_fragment.y+eng.Window.height,
					eng.heroes_simulation[j]->hero_x,
					eng.heroes_simulation[j]->hero_y,
					eng.heroes_simulation[j]->hero_x+1,
					eng.heroes_simulation[j]->hero_y+1
					)==false)
					{
						DestroyInstance(Sound_info_heroes, i);
						break;break;
					}
				}
			}
		}
		sprawdz=false;
	}

	//destroy shots sound
	sprawdz=true;
	while(sprawdz==true)
	{
		for(int i=0;i<Sound_info_shots.size();i++)
		{
			if(al_get_sample_instance_playing(Sound_info_shots[i]->instance)!=true)
			{
				DestroyInstance(Sound_info_shots, i);
				break;
			}
		}
		sprawdz=false;
	}

	sprawdz=true;
	while(sprawdz==true)
	{
		for(int i=0;i<Sound_info_shots.size();i++)
		{
			for(int j=0;j<eng.shots_simulation.size();j++)
			{
				if(eng.shots_simulation[j]->sid==Sound_info_shots[i]->id)
				{
					if(intersect_rectangles(
					eng.Map_fragment.x,
					eng.Map_fragment.y,
					eng.Map_fragment.x+eng.Window.width,
					eng.Map_fragment.y+eng.Window.height,
					eng.shots_simulation[j]->shot_x,
					eng.shots_simulation[j]->shot_y,
					eng.shots_simulation[j]->shot_x+1,
					eng.shots_simulation[j]->shot_y+1
					)==false)
					{
						DestroyInstance(Sound_info_shots, i);
						break; break;
					}
				}
			}	
		}
		sprawdz=false;
	}

	logger::Write("sound::DestroySounds()-end",logger::level::debug);

}

bool sound::intersect_rectangles(int x1,int y1, int x2,int y2, int x3, int y3, int x4, int y4)
{
	//x1,y1,x2,y2 self
	//x3,y3,x4,y4 other
	return !((x3 > x2) || (x4 < x1) || (y3 > y2) || (y4 < y1));
}

void sound::DestroyInstance(vector<sound_info*> &info, int i)
{
	al_stop_sample_instance(info[i]->instance);
	al_detach_sample_instance(info[i]->instance);
	al_destroy_sample_instance(info[i]->instance);
	delete (info[i]);
	info.erase(info.begin()+i);
}