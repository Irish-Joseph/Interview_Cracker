/**
 * Topic: virtual calls during construction, and the Integer cache
 *
 * Two "the compiler let me do it, but it is still a bug" traps:
 *
 *   1. Calling an OVERRIDABLE method from a constructor. Java dispatches
 *      virtually even mid-construction, so the subclass's version runs
 *      BEFORE the subclass has finished initializing - typically printing
 *      base-class field values, and in real code touching fields that are
 *      still at their default values.
 *
 *   2. == on boxed numbers. Integer.valueOf caches -128..127, so within that
 *      range two boxes are literally the same object (== is true) and above
 *      it they are not. == on boxes is object identity, never value equality.
 *
 * Compile: javac VirtualCallInConstructor.java
 * Run:     java VirtualCallInConstructor
 * NOTE: validated by inspection (no JDK on this host); the construction
 * order and cache boundaries were simulated in Python to compute every
 * literal in the expected output below.
 */
public class VirtualCallInConstructor {

    static class Animal {
        String name = "animal";

        Animal() {
            describe();   // trap: this is a VIRTUAL call, made before Dog's
                          // body has even started
        }

        void describe() {
            System.out.println("  name=" + name);
        }
    }

    static class Dog extends Animal {
        Dog() {
            super();      // runs Animal's constructor, which calls describe()
            name = "dog"; // too late for the call above
        }

        @Override
        void describe() {
            System.out.println("  bark, name=" + name);
        }
    }

    public static void main(String[] args) {
        System.out.println("during new Dog():");
        Dog dog = new Dog();
        System.out.println("after construction:");
        dog.describe();

        System.out.println("Integer cache (== compares OBJECTS):");
        Integer a = 127, b = 127;
        Integer c = 128, d = 128;
        System.out.println("a == b (127, cached) : " + (a == b));
        System.out.println("c == d (128, not)    : " + (c == d));
        System.out.println("d.equals(c)          : " + d.equals(c));
    }
}

/*
Expected output:

during new Dog():
  bark, name=animal
after construction:
  bark, name=dog
Integer cache (== compares OBJECTS):
a == b (127, cached) : true
c == d (128, not)    : false
d.equals(c)          : true
*/
