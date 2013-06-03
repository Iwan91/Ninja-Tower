#include "Hero.h"
#include "Functions_HDD.h"
#include "IniReader.h"
#include "../logger.h"


bool Hero::load(string path)
{
	
	//ustawienia bitmap na ALLEGRO_VIDEO_BITMAP
	al_set_new_bitmap_flags(ALLEGRO_VIDEO_BITMAP);

	portrait=al_load_bitmap((path+"\\portarit.bmp").c_str());
	if(!portrait){logger::Write("portrait==NULL",logger::level::fatal_error);return false;};
	ALLEGRO_COLOR color=al_get_pixel(portrait, 0, 0);
	al_convert_mask_to_alpha(portrait, al_map_rgb_f(color.r, color.g,color.b));

	portrait2=al_load_bitmap((path+"\\portarit2.bmp").c_str());
	if(!portrait2){logger::Write("portrait2==NULL",logger::level::fatal_error);return false;};
	ALLEGRO_COLOR color2=al_get_pixel(portrait2, 0, 0);
	al_convert_mask_to_alpha(portrait2, al_map_rgb_f(color2.r, color2.g,color2.b));

	//sprawdzenie czy sciezka jest poprawna po istniejacym pliku infoHero.ini
	if (Functions_HDD::FileExists((path+"\\infoHero.ini").c_str())==true)
	{
		//odczyt info.ini o bohaterze
		CIniReader InfoHero((path+"\\infoHero.ini"));
		name=InfoHero.ReadString("general", "name", "");
		speed=InfoHero.ReadFloat("general","speed",0);
		jump=InfoHero.ReadFloat("general","jump",0);
		mass=InfoHero.ReadFloat("general","mass",0);
		hp=InfoHero.ReadFloat("general","hp",0);
		regen=InfoHero.ReadFloat("general","regen",0);
		
		string shots=InfoHero.ReadString("general", "related_shots", "");
		while(shots.length()!=0)
		{
			related_shots.push_back(atoi(shots.substr(0,shots.find(" ")).c_str()));
			if(shots.find(" ")!=string::npos) shots.erase(0,shots.find(" ")+1);
				else shots.clear();
		}

		string buffs=InfoHero.ReadString("general", "related_buffs", "");
		while(buffs.length()!=0)
		{
			related_buffs.push_back(atoi(buffs.substr(0,buffs.find(" ")).c_str()));
			if(buffs.find(" ")!=string::npos) buffs.erase(0,buffs.find(" ")+1);
				else buffs.clear();
		}

		//wiecej info póŸniej!!!!!!!!!!!!!!!!!!!!!
		CIniReader Skills((path+"\\infoSkills.ini"));

		Skill *new_skill=new Skill();
		new_skill->activation_key="vkey_lpm";
		new_skill->skillID= Skills.ReadInteger("vkey_lpm","skillID",-1);
		new_skill->AnimationHeroID= Skills.ReadInteger("vkey_lpm","AnimationID",-1);
		new_skill->cooldown=Skills.ReadFloat("vkey_lpm","cooldown",-1);
		skills.push_back(new_skill);

		new_skill=new Skill();
		new_skill->activation_key="vkey_ppm";
		new_skill->skillID= Skills.ReadInteger("vkey_ppm","skillID",-1);
		new_skill->AnimationHeroID= Skills.ReadInteger("vkey_ppm","AnimationID",-1);
		new_skill->cooldown=Skills.ReadFloat("vkey_ppm","cooldown",-1);
		skills.push_back(new_skill);

		new_skill=new Skill();
		new_skill->activation_key="vkey_shift";
		new_skill->skillID= Skills.ReadInteger("vkey_shift","skillID",-1);
		new_skill->AnimationHeroID= Skills.ReadInteger("vkey_shift","AnimationID",-1);
		new_skill->cooldown=Skills.ReadFloat("vkey_shift","cooldown",-1);
		skills.push_back(new_skill);

		new_skill=new Skill();
		new_skill->activation_key="vkey_q";
		new_skill->skillID= Skills.ReadInteger("vkey_q","skillID",-1);
		new_skill->AnimationHeroID= Skills.ReadInteger("vkey_q","AnimationID",-1);
		new_skill->cooldown=Skills.ReadFloat("vkey_q","cooldown",-1);
		skills.push_back(new_skill);

		new_skill=new Skill();
		new_skill->activation_key="vkey_e";
		new_skill->skillID= Skills.ReadInteger("vkey_e","skillID",-1);
		new_skill->AnimationHeroID= Skills.ReadInteger("vkey_e","AnimationID",-1);
		new_skill->cooldown=Skills.ReadFloat("vkey_e","cooldown",-1);
		skills.push_back(new_skill);


		//sprawdzenie jakie foldery z animacjami sa
		vector<string> animationsDirs=Functions_HDD::ListOfDirectories(path);
		for(int i=0;i<animationsDirs.size();i++)
		{
			string anim=path+"\\anim"+Functions_HDD::IntToStr(i);
			Animation *animation=new Animation();
			animations.push_back(animation);
			
			animations[i]->sound=al_load_sample((anim+"\\sound.wav").c_str());
			//zczytanie HitBox dla danej animacji i punktu synchro
			CIniReader HitBox((anim+"\\hitbox.ini").c_str());
			animations[i]->synchroPoint_x=HitBox.ReadInteger("synchroPoint","x",0);
			animations[i]->synchroPoint_y=HitBox.ReadInteger("synchroPoint","y",0);
			animations[i]->SpeedOfAnimation=HitBox.ReadFloat("main","SpeedOfAnimation",-1);

			int ilosc_boxow=HitBox.ReadInteger("main","rectangles",0);
			for(int j=0;j<ilosc_boxow;j++)
			{
				Box *box=new Box();
				box->x1=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"x1",0);
				box->x2=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"x2",0);
				box->y1=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"y1",0);
				box->y2=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"y2",0);
				animations[i]->hitboxes.push_back(box);
			}

			//wyszukanie frame*
			vector<string> findFrames=Functions_HDD::Find(anim, "frame");
			for(int j=0;j<findFrames.size();j++)
			{
				Frame *frame=new Frame();
				animations[i]->frames.push_back(frame);
				animations[i]->frames[j]->picture=al_load_bitmap((anim+"\\frame"+Functions_HDD::IntToStr(j)+".bmp").c_str());
				if(!animations[i]->frames[j]->picture)
				{
					animations[i]->frames[j]->picture=al_load_bitmap((anim+"\\frame"+Functions_HDD::IntToStr(j)+".png").c_str());
					
					if(!animations[i]->frames[j]->picture)
					{
						logger::Write((anim+"\\frame"+Functions_HDD::IntToStr(j)+"=NULL").c_str(),logger::level::fatal_error);
						return false;
					}
				};

				//zrobienie tla przeŸroczystego
				ALLEGRO_COLOR color=al_get_pixel(animations[i]->frames[j]->picture, 0, 0);
				al_convert_mask_to_alpha(animations[i]->frames[j]->picture, al_map_rgb_f(color.r, color.g,color.b));

			}
		}
		return true;
	}
	else
	{
		return false;

	}
	
	return true;
}

bool Shot::load(string path)
{
		//ustawienia bitmap na ALLEGRO_VIDEO_BITMAP
		al_set_new_bitmap_flags(ALLEGRO_VIDEO_BITMAP);

		//sprawdzenie jakie foldery z animacjami sa
		CIniReader Info((path+"\\info.ini").c_str());
		has_death_animation=Info.ReadInteger("main","has_death_animation",0);


		vector<string> animationsDirs=Functions_HDD::ListOfDirectories(path);
		for(int i=0;i<animationsDirs.size();i++)
		{
			string anim=path+"\\anim"+Functions_HDD::IntToStr(i);
			Animation *animation=new Animation();
			animations.push_back(animation);

			animations[i]->sound=al_load_sample((anim+"\\sound.wav").c_str());
			//zczytanie HitBox dla danej animacji i punktu synchro
			CIniReader HitBox((anim+"\\hitbox.ini").c_str());
			animations[i]->synchroPoint_x=HitBox.ReadInteger("synchroPoint","x",0);
			animations[i]->synchroPoint_y=HitBox.ReadInteger("synchroPoint","y",0);
			
			animations[i]->SpeedOfAnimation=HitBox.ReadFloat("main","SpeedOfAnimation",-1);
			int ilosc_boxow=HitBox.ReadInteger("main","rectangles",0);
			for(int j=0;j<ilosc_boxow;j++)
			{
				Box *box=new Box();
				box->x1=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"x1",0);
				box->x2=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"x2",0);
				box->y1=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"y1",0);
				box->y2=HitBox.ReadInteger("hitBox"+Functions_HDD::IntToStr(j),"y2",0);
				animations[i]->hitboxes.push_back(box);
			}
		
			//wyszukanie frame*
			vector<string> findFrames=Functions_HDD::Find(anim, "frame");
			for(int j=0;j<findFrames.size();j++)
			{
				Frame *frame=new Frame();
				animations[i]->frames.push_back(frame);
				animations[i]->frames[j]->picture=al_load_bitmap((anim+"\\frame"+Functions_HDD::IntToStr(j)+".bmp").c_str());
				if(!animations[i]->frames[j]->picture)
				{
					animations[i]->frames[j]->picture=al_load_bitmap((anim+"\\frame"+Functions_HDD::IntToStr(j)+".png").c_str());
					
					if(!animations[i]->frames[j]->picture)
					{
						logger::Write((anim+"\\frame"+Functions_HDD::IntToStr(j)+"=NULL").c_str(),logger::level::fatal_error);
						return false;
					}
				};


				//zrobienie tla przeŸroczystego
				ALLEGRO_COLOR color=al_get_pixel(animations[i]->frames[j]->picture, 0, 0);
				al_convert_mask_to_alpha(animations[i]->frames[j]->picture, al_map_rgb_f(color.r, color.g,color.b));

			}
		}

		return true;
}

bool Buff::load(string path)
{
	al_set_new_bitmap_flags(ALLEGRO_VIDEO_BITMAP);

	picture=al_load_bitmap((path+"\\image.bmp").c_str());
	if(!picture) return false;

	return true;
}