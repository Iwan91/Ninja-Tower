#include <stdio.h>
#include <string.h>
#include <allegro5/allegro.h>
#include "../resources/resources.h"
#include "../engine/engine.h"
#pragma once
class keyboard
{
	#define KEYPRESSED	0x1
	#define KEYNEW		0x2
	#define KEYREPEAT	0x4
	public:
		keyboard();
		void keycheck();
		void keydown(ALLEGRO_KEYBOARD_EVENT *kb);
		void keyup(ALLEGRO_KEYBOARD_EVENT *kb) ;
		void keyrepeat(ALLEGRO_KEYBOARD_EVENT *kb);
		void keyupdate();
		char key[256];
	private:
		void keyclear();
		void SendMoveStatus();
		bool change;

};

class mouse
{
	public:
		int x_relative,y_relative;
		int x,y;
		char key[4];
		void keydown(ALLEGRO_MOUSE_EVENT *km);
		void keyup(ALLEGRO_MOUSE_EVENT *km);
};

class input
{  
	public:
        static input& getInstance();
		mouse mouse;
		keyboard keyboard;
		void SendActionKey();
	private:
        input();
        input(const input &);
        input& operator=(const input&);
};