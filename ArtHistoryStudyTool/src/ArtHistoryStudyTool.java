import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import java.util.ArrayList;
import java.util.Random;

public class ArtHistoryStudyTool {
    public static void main(String[] args) throws Exception {
        
        ArrayList<Work> Artworks = new ArrayList<Work>();
        //String[] files = {"GlobalPrehistory.txt", "America.txt", "AncientEgypt.txt"};

        try{
            //for(String s : files){
            for(String s : args){
                File file = new File(s);
                Scanner reader = new Scanner(file);

                while(reader.hasNextLine()){
                    String inp = reader.nextLine();
                    if(inp.equals("endfile")) break;

                    String[] identifiersNew = new String[6];

                    inp += ";";

                    int ct = 0;
                    while(inp.length() != 0){
                        identifiersNew[ct] = inp.substring(0, inp.indexOf(";"));

                        if(inp.indexOf(";") + 1 > inp.length()) break;
                        inp = inp.substring(inp.indexOf(";") + 1);

                        ct++;
                    }

                    Work newWork = new Work(identifiersNew);
                    Artworks.add(newWork);
                }

                reader.close();
            }
        }
        catch(FileNotFoundException e){
            System.out.println("unable to open file");
            e.printStackTrace();
            return;
        }

        System.out.println("Artworks list:");
        for(Work w : Artworks){
            System.out.println("\t" + w.toString());
        }

        learn(Artworks);
    }

    public static void learn(ArrayList<Work> l){
        System.out.println("---------------------");
        System.out.println("Beginning Learn Mode.");
        System.out.println("---------------------");

        Scanner keyboard = new Scanner(System.in);
        Random rand = new Random();

        ArrayList<Work> completedWorks = new ArrayList<Work>();
        ArrayList<Work> currentWorks = new ArrayList<Work>();
        int target = l.size();

        while(l.size() > 0){

            while(currentWorks.size() < 3 && l.size() != 0){
                int targi = rand.nextInt(0, l.size());
                currentWorks.add(l.get(targi));
                l.remove(targi);
            }

            while(currentWorks.size() == 3){
                int targi = rand.nextInt(0, currentWorks.size());
                Work curr = currentWorks.get(targi);

                System.out.println("List the identifiers for " + curr.getName());
                keyboard.nextLine();
                System.out.println(curr.toString());
                // help menu
                System.out.println("If correct, type 'done'. To see number of works remaining, type 'count'. If not, hit enter.");
                String ui = keyboard.nextLine();

                ui = ui.toLowerCase();
                if(ui.equals("done")){
                    completedWorks.add(curr);
                    currentWorks.remove(targi);
                } else if(ui.equals("count")){
                    System.out.println((target - completedWorks.size()) + " works remaining.");
                }
            }

        }
        keyboard.close();

        System.out.println("--------------------");
        System.out.println("Learn mode finished.");
        System.out.println("--------------------");
    }

    public static void test(ArrayList<Work> l){
        System.out.println("---------------");
        System.out.println("Beginning Test.");
        System.out.println("---------------");

        Scanner keyboard = new Scanner(System.in);
        Random rand = new Random();

        while(l.size() > 0){
            int x = rand.nextInt(0, l.size());
            System.out.println("List identifiers for " + l.get(x).getName());
            keyboard.nextLine();
            System.out.println(l.get(x).toString());
            String ui = keyboard.nextLine();
            // help menu
            if(ui.equals("done")){
                System.out.println("Work completed.");
                l.remove(x);
            } else if(ui.equals("count")){
                System.out.println(l.size() + " works remaining.");
            }
        }
        keyboard.close();

        System.out.println("--------------");
        System.out.println("Test finished.");
        System.out.println("--------------");
    }

}



class Work
{
    public String[] identifiers = new String[6];

    public Work(String[] arr){
        for(int i = 0; i < arr.length; i++){
            this.identifiers[i] = arr[i];
        }
    }

    public Work(String n, String a, String d, String c, String m, String p){
        identifiers[0] = n;
        identifiers[1] = a;
        identifiers[2] = d;
        identifiers[3] = c;
        identifiers[4] = m;
        identifiers[5] = p;
    }

    public String getName(){
        return this.identifiers[0];
    }

    public String toString(){
        String res = "";
        for(String s : this.identifiers){
            res += s + ", ";
        }
        return res.substring(0, res.length()-2);
    }
}


