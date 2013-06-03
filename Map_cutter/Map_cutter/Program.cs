using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Drawing;

namespace Test
{
    class Program
    {
        static void Main(string[] args)
        {
            Bitmap b = new Bitmap("map.png");
            int width = b.Width;
            int height = b.Height;

            int klocek_w = 512;
            int klocek_h = 512;

            int ilosc_w = System.Convert.ToInt32(Math.Ceiling((double)width / (double)klocek_w));

            int ilosc_h = System.Convert.ToInt32(Math.Ceiling((double)height / (double)klocek_h));

            int licznik = 0;

            for (int i = 0; i < ilosc_h; i++)
            {
                for (int j = 0; j < ilosc_w; j++)
                {
                    Rectangle src = new Rectangle(j * klocek_w, i * klocek_h, klocek_w, klocek_h);
                    Rectangle dst = new Rectangle(0, 0, klocek_w, klocek_h);

                    int x_temp = 0;
                    int y_temp = 0;
                    if (j * klocek_w + klocek_w >= width)
                    {
                        x_temp = width - j * klocek_w;
                    }
                    else
                    {
                        x_temp = klocek_w;
                    }

                    if (i * klocek_h + klocek_h >= height)
                    {
                        y_temp = height - i * klocek_h;
                    }
                    else
                    {
                        y_temp = klocek_h;
                    }

                    Bitmap temp = new Bitmap(x_temp, y_temp);

                    Graphics g = Graphics.FromImage(temp);
                    g.DrawImage(b, dst, src, GraphicsUnit.Pixel);

                    temp.Save("wynik\\" + Convert.ToString(licznik) + ".png", System.Drawing.Imaging.ImageFormat.Png);
                    licznik++;
                }
            }
        }
    }
}