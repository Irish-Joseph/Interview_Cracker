// Topic: virtual functions and the vtable - and the non-virtual destructor trap
//
// A class with at least one virtual function gets a hidden vtable: one per
// dynamic type, a pointer to it in each object, and each virtual call
// dispatched THROUGH that pointer. That indirection is what makes
// `base->draw()` run the *derived* version - and it is also what makes
// deleting a polymorphic object through a base pointer UNDEFINED BEHAVIOUR
// when the base destructor is not virtual.
//
// Concepts:
//   - virtual dispatch: the call is resolved at RUNTIME from the object's
//     actual type, not the static type of the pointer
//   - the vtable is per-CLASS (shared by all instances), the vptr is per-OBJECT
//   - hiding vs overriding: a non-virtual function with the same name in the
//     derived class HIDES the base one - no error, no warning, wrong call
//   - virtual destructor: if you intend delete-through-base, the base
//     destructor MUST be virtual (or the whole derived part is skipped)
//   - pure virtual (= 0) makes the class abstract; the class can still have
//     normal, virtual, and non-virtual members
//
// Compile: g++ -std=c++17 -Wall -o virtual_vtable virtual_vtable.cpp
// NOTE: validated by inspection (no C++ toolchain on this host). The
// non-virtual-destructor case is UB by definition, so the program comments
// it out and explains it instead of executing undefined behaviour.

#include <iostream>
#include <string>

// Base with one virtual call, one NON-virtual (to show hiding), and - for
// contrast - a SECOND class hierarchy below with a NON-virtual destructor.
class Animal {
public:
    virtual ~Animal() = default;   // virtual: deleting through Animal* is safe

    virtual void speak() const { std::cout << "  (generic animal sound)" << std::endl; }

    // Deliberately NOT virtual: derived classes can HIDE this, which compiles
    // fine but is a classic bug source.
    void label() const { std::cout << "  label from Animal" << std::endl; }
};

class Dog : public Animal {
public:
    void speak() const override { std::cout << "  woof" << std::endl; }   // override
    void label() const { std::cout << "  label from Dog (HIDES Animal::label)" << std::endl; }
};

class Cat : public Animal {
public:
    void speak() const override { std::cout << "  meow" << std::endl; }
    // Cat does NOT override label(), so a Cat still calls Animal::label.
};

// The trap, isolated in its own hierarchy so its UB never runs:
class Widget {
public:
    ~Widget() { std::cout << "  ~Widget" << std::endl; }   // NOT virtual
};

class Gadget : public Widget {
    std::string payload;   // the derived part that a non-virtual base dtor skips
public:
    Gadget() : payload("gadget-data") {}
    ~Gadget() { std::cout << "  ~Gadget (frees " << payload.size() << " bytes of payload)" << std::endl; }
};

int main() {
    std::cout << "== virtual dispatch through a base pointer ==" << std::endl;
    Animal* zoo[3] = { new Dog, new Cat, new Animal };
    for (Animal* a : zoo) a->speak();     // each call picks the DYNAMIC type

    std::cout << "== hiding, not overriding (the non-virtual one) ==" << std::endl;
    Dog* asDog = new Dog;
    Animal* viaBase = asDog;
    viaBase->label();                     // "label from Animal" - the base version!
    asDog->label();                        // only a Dog*-typed call sees Dog::label
    std::cout << "  (hiding is chosen by the STATIC type of the expression)" << std::endl;

    std::cout << "== why the base destructor must be virtual ==" << std::endl;
    // 'asDog' and 'viaBase' name the SAME object, so this loop deletes every
    // animal exactly once. Because ~Animal is virtual, deleting through the
    // Animal* runs ~Dog (or ~Cat) first, then ~Animal:
    for (Animal* a : zoo) delete a;       // safe: base dtor is virtual
    delete asDog;                          // the extra Dog from the hiding demo

    // The non-virtual case, commented out because it is UNDEFINED BEHAVIOUR:
    //
    //   Widget* w = new Gadget;
    //   delete w;
    //
    // What actually happens in practice: ~Widget runs, ~Gadget NEVER runs,
    // and the Gadget's string member leaks. Some toolchains warn about this
    // (-Wdelete-non-virtual-dtor); ASan flags it. The fix is one keyword:
    // make ~Widget virtual. The rule: if a class is meant to be deleted
    // through a base pointer, its destructor must be virtual (or the class
    // should be made final/non-polymorphic and never derived from).

    return 0;
}

/*
Expected output:

== virtual dispatch through a base pointer ==
  woof
  meow
  (generic animal sound)

== hiding, not overriding (the non-virtual one) ==
  label from Animal
  label from Dog (HIDES Animal::label)
  (hiding is chosen by the STATIC type of the expression)

== why the base destructor must be virtual ==
  ~Dog
  ~Cat
  ~Dog
*/
