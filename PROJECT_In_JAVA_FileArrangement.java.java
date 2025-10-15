import java.io.*;

class NotADirectoryException extends Exception
{
	NotADirectoryException(String msg)
	{
		super(msg);
	}
}
class Arrange
{
	File dir;
	public Arrange(String filename) throws NotADirectoryException
	{
		dir = new File(filename);
		if(!dir.isDirectory() | !dir.exists())
		{
			NotADirectoryException n = new NotADirectoryException("Given name is not a directory name!");
			throw n;
		}
	}
	public void transfer()
	{
		File Dir = new File(dir.toString(),"Directories");
		if(!Dir.exists())
		{
			Dir.mkdir();					
		}
		File listFile[] = dir.listFiles(); 
		for(File f:listFile)
		{
			if(f.isDirectory())
			{
				File f2 = new File(Dir.toString(),f.getName());
				f.renameTo(f2);	
			}
			else if(f.isFile())
			{
				String fname = f.toString();
				for(int i=0;i<fname.length();i++)
				{
					if(fname.charAt(i)=='.')
					{
						String str = fname.substring(i+1);
						File fol = new File(Dir.toString(),str);
						if(!fol.exists())
						{
							fol.mkdir();
						}
						File f2 = new File(fol.toString(),f.getName());
						f.renameTo(f2);	
						break;
					}
				}
			}
		}
		try
		{
			System.out.println("......Processing.....");
			Thread.sleep(2000);
		}
		catch(InterruptedException e)
		{
			System.out.println(e);
		}
		System.out.println("Transfer completed successfully");
	}
}
public class Project
{
	public static void main(String args[])
	{
		if(args.length>0)
		{
			try
			{
				Arrange obj = new Arrange(args[0]);
				obj.transfer();
			}
			catch(NotADirectoryException n)
			{
				System.out.println(n);
			}
		}
		else
		{
			System.out.println("Please enter a Directory name as an argument next time");
		}
		
	}
}