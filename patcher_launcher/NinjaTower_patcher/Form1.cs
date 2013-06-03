using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
//using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO;
using System.Net;

namespace NinjaTower_patcher
{  
    public partial class Form1 : Form
    {
        WebClient webClient;

        Int64 progressChunk = 0;
        public void DownloadProgressChanged(Object sender,  DownloadProgressChangedEventArgs e)
        {
            progressChunk = e.ProgressPercentage;
        }
        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Shown(object sender, EventArgs e)
        {
            BringToFront();

            webBrowser1.Navigate("http://www.ninjatower.eu/patcher/news.html");

            webClient = new WebClient();
            //webClient.Headers.Add("user-agent", "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.2; .NET CLR 1.0.3705;)");
            webClient.DownloadProgressChanged += new DownloadProgressChangedEventHandler(this.DownloadProgressChanged);

            backgroundWorker1.RunWorkerAsync();
        }

        private void generate_data()
        {
            label1.Invoke(new Action(() =>
            {
                label1.Text = "Scanning files...";
            }
            ));

            files.Clear();
            folders.Clear();

            string path = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);

            if (!Directory.Exists(path + "\\data\\")) Directory.CreateDirectory(path + "\\data\\");
            DirectoryInfo di = new DirectoryInfo(path+"\\data\\");
            FullDirList(di, "*");

            StreamWriter zapis = new StreamWriter(path+"\\client_data.dat");
            for (int i = 0; i < files.Count; i++)
            {
                zapis.WriteLine(GetRelativePath( path,files[i].FullName) + " " + files[i].Length + " " + files[i].LastWriteTimeUtc);
            }
            zapis.Close();

            progressBar1.Invoke(new Action(() =>
            {
                progressBar1.Value = 10;
            }
            ));
        }

        private void get_data()
        {
            label1.Invoke(new Action(() =>
            {
                label1.Text = "Download server data...";
            }
            ));
            string path = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);

            webClient.DownloadFile("http://ninjatower.eu/patcher/server_data.dat", path + "\\server_data.dat");

            progressBar1.Invoke(new Action(() =>
            {
                progressBar1.Value = 20;
            }
            ));
        }

        private struct dane
        {
            public string path;
            public long size;
            public DateTime data;
        };
        List<dane> client = new List<dane>();
        List<dane> server = new List<dane>();

        private void load_client_data()
        {
            client.Clear();
            
            string path = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);

            StreamReader client_p = new StreamReader(path + "\\client_data.dat");
            while (!client_p.EndOfStream)
            {
                string tmp = client_p.ReadLine();

                dane tmp2 = new dane();
                tmp2.path = tmp.Substring(0, tmp.IndexOf(' '));
                tmp = tmp.Remove(0, tmp.IndexOf(' ') + 1);
                tmp2.size = Convert.ToInt64(tmp.Substring(0, tmp.IndexOf(' ')));
                tmp = tmp.Remove(0, tmp.IndexOf(' ') + 1);
                tmp2.data=DateTime.SpecifyKind(DateTime.Parse(tmp), DateTimeKind.Utc);

                client.Add(tmp2);
            }
            client_p.Close();
            System.IO.File.Delete(path + "\\client_data.dat");

        }

        private void load_server_data()
        {
            server.Clear();
            string path = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);

            StreamReader server_p = new StreamReader(path + "\\server_data.dat");
            while (!server_p.EndOfStream)
            {
                string tmp = server_p.ReadLine();

                dane tmp2 = new dane();
                tmp2.path = tmp.Substring(0, tmp.IndexOf(' '));
                tmp = tmp.Remove(0, tmp.IndexOf(' ') + 1);
                tmp2.size = Convert.ToInt64(tmp.Substring(0, tmp.IndexOf(' ')));
                tmp = tmp.Remove(0, tmp.IndexOf(' ') + 1);
                tmp2.data = DateTime.SpecifyKind(DateTime.Parse(tmp),DateTimeKind.Utc);

                server.Add(tmp2);
            }
            server_p.Close();
            System.IO.File.Delete(path + "\\server_data.dat");
 
        }

        private void update()
        {
            label1.Invoke(new Action(() =>
            {
                label1.Text = "Calculate differences...";
            }
            ));

            List<dane> diff = new List<dane>();
            List<dane> diff2 = new List<dane>();

            load_client_data();
            load_server_data();

            string path = System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);

            
            //co serwer ma a czego nie ma klient
            Int64 max_size = 0;
            for (int i = 0; i < server.Count; i++)
            {
                bool znal=false;
                for (int j = 0; j<client.Count; j++)
                {
                    if ((server[i].path == client[j].path &&
                         server[i].size == client[j].size ) == true)
                    {
                        if (server[i].data.CompareTo(client[j].data) == 0)
                        {
                            znal = true;
                        }
                    }
                }

                if (znal == false)
                {
                    diff.Add(server[i]);
                    max_size = max_size + server[i].size;
                }
            }

            Int64 size = 0;
            for (int i = 0; i < diff.Count; i++)
            {
                try
                {
                    string path2 = diff[i].path.Replace('\\', '/');
                    label1.Invoke(new Action(() =>
                    {
                        label1.Text = "Download: " + diff[i].path;
                    }
                    ));

                    if (!Directory.Exists(Directory.GetParent(diff[i].path).FullName))
                    {
                        Directory.CreateDirectory(Directory.GetParent(diff[i].path).FullName);
                    }

                    if (File.Exists(diff[i].path)) File.Delete(diff[i].path);

                    Uri uri = new Uri("http://ninjatower.eu/patcher/" + path2);
                    webClient.DownloadFileAsync(uri, path + "\\" + diff[i].path);
                    Int64 temp_size = 0;
                    while (webClient.IsBusy == true)
                    {
                        System.Threading.Thread.Sleep(1000);
                        temp_size = Convert.ToInt64((double)diff[i].size * ((double)progressChunk / 100.0));

                        label2.Invoke(new Action(() =>
                        {
                            String x = String.Format("{0:0.00}", (Math.Round((double)(size + temp_size) / 1000000, 2)));
                            String y = String.Format("{0:0.00}", (Math.Round((double)max_size / 1000000, 2)));
                            label2.Text = x + "/" + y + " MB";
                        }
                        ));

                        progressBar1.Invoke(new Action(() =>
                        {
                            double dzielnik = 1.0 / (diff.Count + 1.0);
                            progressBar1.Value = Convert.ToInt32(20.0 + 60 * dzielnik * i);
                        }
                        ));
                    }
                    System.IO.File.SetLastWriteTimeUtc(path + "\\" + diff[i].path, diff[i].data);

                    size = size + diff[i].size;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Error");
                    continue;
                }
            }

            label2.Invoke(new Action(() =>
            {
                label2.Text = "";
            }
            ));

            generate_data();
            load_client_data();

            for (int i = 0; i < client.Count; i++)
            {
                bool znal = false;
                for (int j = 0; j < server.Count; j++)
                {
                    if ((client[i].path == server[j].path &&
                        client[i].size == server[j].size
                       ) == true)
                    {
                        znal = true;
                    }
                }

                if (znal == false)
                {
                    diff2.Add(client[i]);
                }
            }

            for (int i = 0; i < diff2.Count; i++)
            {
                label1.Invoke(new Action(() =>
                {
                    label1.Text = "Delete: " + diff2[i].path;
                }
                ));

                File.Delete(path + "\\" + diff2[i].path);
                if (Directory.GetFiles(Directory.GetParent(diff2[i].path).FullName).Length == 0)
                {
                    Directory.Delete(Directory.GetParent(diff2[i].path).FullName);
                }
            }

            if (diff.Count == 0 && diff2.Count==0) change = false;

            progressBar1.Invoke(new Action(() =>
            {
                progressBar1.Value = 80;
            }
            ));

        }

        static List<FileInfo> files = new List<FileInfo>();  // List that will hold the files and subfiles in path
        static List<DirectoryInfo> folders = new List<DirectoryInfo>(); // List that hold direcotries that cannot be accessed     
        static void FullDirList(DirectoryInfo dir, string searchPattern)
        {

            // Console.WriteLine("Directory {0}", dir.FullName);
            // list the files
            try
            {
                foreach (FileInfo f in dir.GetFiles(searchPattern))
                {
                    //Console.WriteLine("File {0}", f.FullName);
                    files.Add(f);
                }
            }
            catch
            {
               MessageBox.Show("Directory {0}  \n could not be accessed!!!!", dir.FullName);
               Application.Exit();
               return;  // We alredy got an error trying to access dir so dont try to access it again
            }

            // process each directory
            // If I have been able to see the files in the directory I should also be able 
            // to look at its directories so I dont think I should place this in a try catch block
            foreach (DirectoryInfo d in dir.GetDirectories())
            {
                folders.Add(d);
                FullDirList(d, searchPattern);
            }

        }
        private string GetRelativePath(string rootPath, string fullPath)
        {
            if (String.IsNullOrEmpty(rootPath) || String.IsNullOrEmpty(fullPath))
            {
                return null;
            }
            else if (fullPath.Equals(rootPath))
            {
                return string.Empty;
            }
            else if (fullPath.Contains(rootPath + "\\"))
            {
                return fullPath.Substring(rootPath.Length + 1);
            }
            else
            {
                return null;
            }
        }

        bool change = true;
        private void backgroundWorker1_DoWork(object sender, DoWorkEventArgs e)
        {
            while (change == true)
            {
                // generate directories
                generate_data();

                // get directories from server
                get_data();

                // get files from server if diffrent 
                update();
                
            }

                label1.Invoke(new Action(() =>
                {
                    label1.Text = "Done";
                }
                ));

                progressBar1.Invoke(new Action(() =>
                {
                    progressBar1.Value = 100;
                }
                 ));

                button1.Invoke(new Action(() =>
                {
                    button1.Visible = true;
                }
                ));
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string strCmdText;
            strCmdText = "update_ok_go";

            System.Diagnostics.Process p = new System.Diagnostics.Process();
            p.StartInfo.UseShellExecute = false;
            p.StartInfo.FileName = "data\\NinjaTowerLauncher.exe";
            p.StartInfo.WorkingDirectory = "data\\";
            p.StartInfo.Arguments = strCmdText;
            p.Start();

            Environment.Exit(0);
        }

        private void webBrowser1_DocumentCompleted(object sender, WebBrowserDocumentCompletedEventArgs e)
        {
            webBrowser1.Show();
        }
    }
}
