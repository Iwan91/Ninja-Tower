#include <iostream>
#include <string>
#include<windows.h>
#include "sha1.h"
#include <vector>
#include <sstream>
using namespace std;
#pragma once
class communication
{
	  public:
			static communication& getInstance();
			void SetConnection(string login, string password, string ip, string portTCP, string portUDP);
			void Connect();

			void SendTCP(string text2);
			string ReceiveTCP();
			void TCPNonBlocking(DWORD nonBlocking);

			void SendUDP(string text);
			string ReceiveUDP();
			void UDPNonBlocking(DWORD nonBlocking);

			void SendReady();


	  private:
			communication();
			communication(const communication &);
			communication& operator=(const communication&);

			string login;
			string password;
			string ip;
			string portTCP;
			string portUDP;
			SOCKET m_socket;
			SOCKET UDP_socket;
			SOCKADDR_IN UDP_addr;

			bool ConnectTCP_UDP();
			bool SecureTCP();
			int HexToInt(char a,char b);
			void IntToHex(unsigned char byte, char * hex);
			string GetSHA1(string text);
			vector<string> split(string text,char separator);
			string ToLowerCase(string text);
};