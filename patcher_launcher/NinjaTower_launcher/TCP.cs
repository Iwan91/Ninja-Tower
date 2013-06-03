using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Net.Sockets;
using System.Net.Security;
using System.Windows.Forms;
using System.Security.Cryptography.X509Certificates;
using System.Net;
using System.Web.Script.Serialization;
using Newtonsoft.Json.Linq;
using System.Security.Cryptography;

namespace NinjaTower_launcher
{

    sealed class TCP
    {
        private static TCP instance = new TCP();
        private TCP()
        {
        }
        static TCP()
        {
        }
        public static TCP Instance
        {
            get
            {
                return instance;
            }
        }
        TcpClient socket;
        SslStream sslStream;
        static bool CertificateValidationCallback(object sender, X509Certificate certificate, X509Chain chain, SslPolicyErrors sslPolicyErrors)
        {
            return true;
        }
        public void connect()
        {
            try
            {
                socket = new TcpClient();
                socket.Connect("s1.in.henrietta.com.pl", 4001);
                sslStream = new SslStream(socket.GetStream(), false, new RemoteCertificateValidationCallback(CertificateValidationCallback));
                sslStream.AuthenticateAsClient("s1.in.henrietta.com.pl");
            }
            catch
            {
                MessageBox.Show("Server is offline. Try again later.");
                Environment.Exit(0);
            }

        }

        public string recieve()
        {
  
            int bytes = -1;
            byte[] buffer = new byte[4];
            string odp = "";
            
            bytes = sslStream.Read(buffer, 0, buffer.Length);      

            if (bytes > -1)
            {
                Array.Reverse(buffer);
                byte[] buffer2 = new byte[BitConverter.ToUInt32(buffer,0)];
                bytes=sslStream.Read(buffer2, 0, buffer2.Length);
                odp = Convert.ToString(Encoding.UTF8.GetString(buffer2, 0, bytes));

             }
 
            return odp;
        }

        public void send(string text)
        {

            byte[] length = BitConverter.GetBytes(Encoding.UTF8.GetByteCount(text));
            Array.Reverse(length);

            System.Text.UTF8Encoding enc = new System.Text.UTF8Encoding();
            byte[] text2=enc.GetBytes(text);

            byte[] send=new byte[length.Length + text2.Length];
            length.CopyTo(send, 0);
            text2.CopyTo(send, length.Length);

            sslStream.Write(send);
        }

        public void send_login(string login, string password)
        {
            byte[] buffer = Encoding.UTF8.GetBytes(login.ToLower()+password);
            SHA1CryptoServiceProvider cryptoTransformSHA1 =
            new SHA1CryptoServiceProvider();
            string hash = BitConverter.ToString(cryptoTransformSHA1.ComputeHash(buffer)).Replace("-", "");

            string text = "{\"login\" : \""+login+"\",\"password\" : \""+hash+"\"}";
            send(text);

            string msgJSON = "";
            while (true)
            {
                msgJSON = TCP.Instance.recieve();
                if (msgJSON != "") break;
                Application.DoEvents();
            }
            
            
            JObject jsonObj = JObject.Parse(msgJSON);
            string status = (string)(jsonObj["status"]);

            if (status == "ok")
            {
                Data.Instance.form1.backgroundWorkerTCP.RunWorkerAsync();

                Data.Instance.form1.Visible = false;

                Data.Instance.form2 = new Form2();

                TCP.Instance.send_server_statistics();

            }
            if (status == "fail")
            {
                Data.Instance.form1.pictureBox1.Visible = true;
                Data.Instance.form1.button1.Visible = true;
            }
        }

        public void ping()
        {
            send("");
        }

        public void send_server_statistics()
        {
            string text = "{\"operation\" : \"server_statistics\"}";
            TCP.Instance.send(text);
        }
    }
   
}
