#include <string>
#include <vector>
#include <allegro5/allegro.h>
#include <allegro5/allegro_audio.h>
#include <allegro5/allegro_acodec.h>
using namespace std;

#pragma once
class Box
{
	public:
		int x1,y1;
		int x2,y2;
};

class Frame
{
	public:
		ALLEGRO_BITMAP *picture;
};

class Animation
{
	public:
		vector<Frame*> frames;
		vector<Box*> hitboxes;
		int synchroPoint_x;
		int synchroPoint_y;
		float SpeedOfAnimation;
		ALLEGRO_SAMPLE *sound;
};

class Shot
{
	public:
		int id;
		vector<Animation*> animations;
		int synchroPoint_x;
		int synchroPoint_y;
		bool load(string path);
		int has_death_animation;
};

class Skill
{
	public:
		string activation_key;
		int AnimationHeroID;
		int skillID;
		float cooldown;
};

class Buff
{
	public:
		int id;
		ALLEGRO_BITMAP *picture;
		bool load(string path);
};

class Hero
{
	public:
		vector<Animation*> animations;
		bool load(string path);

		string name;
		vector<int> related_shots;
		vector<int> related_buffs;
		float speed;
		float jump;
		float mass;
		float hp;
		float regen;
		vector <Skill*> skills;

		ALLEGRO_BITMAP *portrait;
		ALLEGRO_BITMAP *portrait2;
};