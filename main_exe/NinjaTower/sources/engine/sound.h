#include <allegro5/allegro.h>
#include <allegro5/allegro_acodec.h>
#include <allegro5/allegro_audio.h>
#include <vector>
#include <string>
using namespace std;
#pragma once
class sound_info
{
	public:
		int id;
		ALLEGRO_SAMPLE_INSTANCE *instance;
		int id_animation;
};

class sound
{
	public:
		static sound& getInstance();
		void PlaySounds();
	private:
		sound();
        sound(const sound &);
        sound& operator=(const sound&);
		vector<sound_info*> Sound_info_heroes;
		vector<sound_info*> Sound_info_shots;
		void GenerateList();
		void PlayList();
		void DestroySounds();
		bool intersect_rectangles(int x1,int y1, int x2,int y2, int x3, int y3, int x4, int y4);
		void DestroyInstance(vector<sound_info*> &info, int i);
		ALLEGRO_SAMPLE_INSTANCE *theme;
};