public class call_sites {
    public static int methodOne {
        return 1;
    }

    public static int methodTwo {
        return 2;
    }

    public static void main(String args[]) {
        System.out.println(methodOne());

        if (1 = 1) {
            System.out.println(methodTwo());
        }
    }
}