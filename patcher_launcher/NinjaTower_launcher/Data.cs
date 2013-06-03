using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Newtonsoft.Json.Linq;

namespace NinjaTower_launcher
{
    sealed class Data
    {
        private static readonly Data instance = new Data();
        private Data()
        {
        }
        static Data()
        {
        }
        public static Data Instance
        {
            get
            {
                return instance;
            }
        }

        public string login;
        public string password;
        public string TCP, IP, UDP;
        public Form1 form1;
        public Form2 form2;
        public JArray team1,team2,heroes;
        public Form3 form3;
        public Form4 form4;

        public void  start_main_game()
        {
            string strCmdText;
            strCmdText = Data.Instance.login + " " + Data.Instance.password + " " + Data.Instance.IP + " " + Data.Instance.TCP + " " + Data.Instance.UDP + " 0 0";

            System.Diagnostics.Process p = new System.Diagnostics.Process();
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.FileName = "data\\NinjaTower.exe";
            p.StartInfo.WorkingDirectory = "data\\";
            p.StartInfo.Arguments = strCmdText;
            p.Start();
        }

    }
}
