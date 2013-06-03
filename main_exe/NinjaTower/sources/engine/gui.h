#include <vector>
#include <Math.h>
#include <string>
#include <sstream>
using namespace std;
#pragma once

class FPS_counter
{
	public:
		double old_time;
		double fps;
		double frames_done;
};

class gui
{
	public:
		static gui& getInstance();
		void DrawGUI();
	private:
		gui();
        gui(const gui &);
        gui& operator=(const gui&);
		void NavigationDraw();
		vector<int> punkt_przeciecia(int A_x,int A_y,int B_x,int B_y,int maxX, int maxY);
		void DrawFpsCounter();
		FPS_counter FPS_counter;
		void DrawPing();
		void DrawBottom();
		void DrawTop();
		void DrawHeroInfo();
		void DrawBuffs();

};