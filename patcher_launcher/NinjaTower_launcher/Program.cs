using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace NinjaTower_launcher
{
    static class Program
    {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args)
        {
            if (args.Length == 1 && args[0] == "update_ok_go")
            {
                Application.EnableVisualStyles();

                Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(Data.Instance.form1 = new Form1());
            }
        }
    }
}
