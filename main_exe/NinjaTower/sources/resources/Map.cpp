#include "Map.h"
#include "Functions_HDD.h"
#include "IniReader.h"
#include "../logger.h"

bool Map::load(string path)
{
	//ustawienia bitmap na ALLEGRO_VIDEO_BITMAP 
	al_set_new_bitmap_flags(ALLEGRO_VIDEO_BITMAP);

	/*al_set_new_bitmap_flags( ALLEGRO_NO_PREMULTIPLIED_ALPHA );
	al_set_blender(ALLEGRO_ADD, ALLEGRO_ALPHA, ALLEGRO_INVERSE_ALPHA);*/

	sound=al_load_sample((path+"\\sound.ogg").c_str());

	if (Functions_HDD::FileExists((path+"\\info.ini").c_str())==true)
	{
		CIniReader Info((path+"\\info.ini"));
		MapName=Info.ReadString("Main","MapName","");
		Height=Info.ReadInteger("Main","Height",-1);
		Width=Info.ReadInteger("Main","Width",-1);
		
		int teams=2;
		for(int i=0;i<teams;i++)
		{
			SpawnTeam team;
			team.x=Info.ReadInteger("Team"+Functions_HDD::IntToStr(i),"SpawnX",-1);
			team.y=Info.ReadInteger("Team"+Functions_HDD::IntToStr(i),"SpawnY",-1);

			spawnTeams.push_back(team);
		}

		int platforms_int=Info.ReadInteger("Main","Platforms",-1);
		for(int i=0;i<platforms_int;i++)
		{
			Platform platform;
			platform.x1=Info.ReadInteger("Platform"+Functions_HDD::IntToStr(i),"X",-1);
			platform.y=Info.ReadInteger("Platform"+Functions_HDD::IntToStr(i),"Y",-1);
			platform.width=Info.ReadInteger("Platform"+Functions_HDD::IntToStr(i),"Width",-1);
			platform.x2=platform.x1+platform.width;

			platforms.push_back(platform);
		}

		int obstacle_int=Info.ReadInteger("Main","Obstacles",-1);
		for(int i=0;i<obstacle_int;i++)
		{
			Obstacle obstacle;
			obstacle.x1=Info.ReadInteger("Obstacle"+Functions_HDD::IntToStr(i),"X1",-1);
			obstacle.y1=Info.ReadInteger("Obstacle"+Functions_HDD::IntToStr(i),"Y1",-1);
			obstacle.x2=Info.ReadInteger("Obstacle"+Functions_HDD::IntToStr(i),"X2",-1);
			obstacle.y2=Info.ReadInteger("Obstacle"+Functions_HDD::IntToStr(i),"Y2",-1);
			
			obstacles.push_back(obstacle);
		}

		vector<string> paths=Functions_HDD::Find(path, ".png");

		for(int i=0;i<paths.size();i++)
		{
			ALLEGRO_BITMAP* picture=al_load_bitmap((path+"\\"+Functions_HDD::IntToStr(i)+".png").c_str());
			if(!picture){logger::Write("map_picture_"+Functions_HDD::IntToStr(i)+"==NULL",logger::level::fatal_error);return false;}
			
			pictures.push_back(picture);
		}


		return 1;
	}


	return 0;
}