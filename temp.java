public class temp{
    public static void main(String[] args) {
        int chicken = 2;
        int cow = 1;
        for (int i = 0; i < 10; i++) {
            chicken *= 4;
            cow *= 2;
            System.out.println("day " + i);
            System.out.println(chicken);
            System.out.println(cow);
        }
        System.out.println(chicken);
        System.out.println(cow);
        System.out.println(chicken + cow);
    }
}