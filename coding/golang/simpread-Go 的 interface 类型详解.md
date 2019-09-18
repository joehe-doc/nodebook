> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 http://zuozuohao.github.io/2016/06/16/Interfaces-the-awesomesauce-of-Go/

让我们重新梳理一下以前的内容。我们了解了基本的数据类型，我们学习了如何利用已有的数据类型构造出一个新的数据类型。我们学习了基本的控制流语句，我们将要结合这些知识构建一些简单的应用程序。

(本文章翻译自《Let’s learn Go》的 “Interfaces: the awesomesauce of Go” 一节，原文地址：http://go-book.appspot.com/interfaces.html。)

接下来我们会发现函数实际上也是一种数据，他们具有自己的值和类型。我们将要学习关于方法的基本知识。我们使用方法来构建作用于数据上的函数，从而使某个数据类型完成特定的功能。

在本章中，将要学习一个新的领域。我们将学习使用面向对象编程的灵魂去构建程序，让我们一起做这件事吧。

**What is an interface?**

简单的说，接口就是一组方法签名的集合。我们使用一个接口来识别一个对象的能够进行的操作。

举例来说，在以前的章节中，我们看到 Student 和 Emlpoyee 都可以执行 SayHi 函数，但是他们的运行结构是不同的，但是这个是无关紧要的，本质是他们都可以说 “Hi”（这部分下边的内容会有体现）。

我们假设 Student 和 Employee 实现了另外一个共同的函数 Sing。Employ 实现了 SpendSalary 函数，与此相对应 Student 实现了 BorrowMoney 函数。

所以 Student 实现了 SayHi、Sing 和 BorrowMoney 函数，Employee 实现了 SayHi、Sing 和 SpendSalary 函数。

这些方法的集合就是 Student 和 Employee 满足的接口类型。举例来说，Student 和 Employee 都满足包含 SayHi 和 Sing 方法签名的接口。但是 Employee 不能满足包含 SayHi、Sing 和 BorrowMoney 的接口类型，因为 Employee 没有实现方法 BorrowMoney。

**The interface type**

接口类型实际上是一组方法签名的清单，我们将遵循下面的接口约束：

```
type Human struct {
    name string
    age int
    phone string
}

type Student struct {
    Human //an anonymous field of type Human
    school string
    loan float32
}

type Employee struct {
    Human //an anonymous field of type Human
    company string
    money float32
}

// A human likes to stay... err... *say* hi
func (h *Human) SayHi() {
    fmt.Printf("Hi, I am %s you can call me on %s\n", h.name, h.phone)
}

// A human can sing a song, preferrably to a familiar tune!
func (h *Human) Sing(lyrics string) {
    fmt.Println("La la, la la la, la la la la la...", lyrics)
}

// A Human man likes to guzzle his beer!
func (h *Human) Guzzle(beerStein string) {
    fmt.Println("Guzzle Guzzle Guzzle...", beerStein)
}

// Employee's method for saying hi overrides a normal Human's one
func (e *Employee) SayHi() {
    fmt.Printf("Hi, I am %s, I work at %s. Call me on %s\n", e.name,
        e.company, e.phone) //Yes you can split into 2 lines here.
}

// A Student borrows some money
func (s *Student) BorrowMoney(amount float32) {
    loan += amount // (again and again and...)
}

// An Employee spends some of his salary
func (e *Employee) SpendSalary(amount float32) {
    e.money -= amount // More vodka please!!! Get me through the day!
}

// INTERFACES
type Men interface {
    SayHi()
    Sing(lyrics string)
    Guzzle(beerStein string)
}

type YoungChap interface {
    SayHi()
    Sing(song string)
    BorrowMoney(amount float32)
}

type ElderlyGent interface {
    SayHi()
    Sing(song string)
    SpendSalary(amount float32)
}
```

正如你所看到的那样，一个接口可以被任意数量的类型满足，在这里 Student 和 Employee 都实现了 Men 接口。

并且，一个类型可以实现任意数量的接口，在这里，Student 实现了 Men 和 YoungChap 接口，Employee 实现了 Men 和 ElderlyGent 接口。

最后需要说明的是，每个类型都实现了一个空接口 interface{}，大概你要说，这意味着该类型没有方法，我们重新声明一下 interface{} 的意义。

你可能自以为发现接口类型的意义： _非常酷，接口类型的意义就是描述数据类型的行为，以及数据类型的共性特征_

然而事实上，接口类型的意义远远不止于此。

顺便说一下，我说过空接口意味着不包含方法签名吗？

**Interface values**

因为接口也是一种类型，你会困惑于一个接口类型的值到底是什么。

有一个好消息就是：如果你声明了一个接口变量，这个变量能够存储任何实现该接口的对象类型。

也就是说，如果我们声明了 Men 类型的接口变量 m，那么这个变量就可以存储 Student 和 Employee 类型的对象，还有 Human 类型（差点忘掉）。这是因为他们都实现了 Men 接口声明的方法签名。

如果 m 能够存储不同数据类型的值，我们可以轻松实现一个 Men 切片，该切片包含不同的数据类型的实例。

下面这个例子能够帮助梳理我们上面的说教：

```
package main
import "fmt"

type Human struct {
    name string
    age int
    phone string
}

type Student struct {
    Human //an anonymous field of type Human
    school string
    loan float32
}

type Employee struct {
    Human //an anonymous field of type Human
    company string
    money float32
}

//A human method to say hi
func (h Human) SayHi() {
    fmt.Printf("Hi, I am %s you can call me on %s\n", h.name, h.phone)
}

//A human can sing a song
func (h Human) Sing(lyrics string) {
    fmt.Println("La la la la...", lyrics)
}

//Employee's method overrides Human's one
func (e Employee) SayHi() {
    fmt.Printf("Hi, I am %s, I work at %s. Call me on %s\n", e.name,
        e.company, e.phone) //Yes you can split into 2 lines here.
}

// Interface Men is implemented by Human, Student and Employee
// because it contains methods implemented by them.
type Men interface {
    SayHi()
    Sing(lyrics string)
}

func main() {
    mike := Student{Human{"Mike", 25, "222-222-XXX"}, "MIT", 0.00}
    paul := Student{Human{"Paul", 26, "111-222-XXX"}, "Harvard", 100}
    sam := Employee{Human{"Sam", 36, "444-222-XXX"}, "Golang Inc.", 1000}
    Tom := Employee{Human{"Sam", 36, "444-222-XXX"}, "Things Ltd.", 5000}

    //a variable of the interface type Men
    var i Men

    //i can store a Student
    i = mike
    fmt.Println("This is Mike, a Student:")
    i.SayHi()
    i.Sing("November rain")

    //i can store an Employee too
    i = Tom
    fmt.Println("This is Tom, an Employee:")
    i.SayHi()
    i.Sing("Born to be wild")

    //a slice of Men
    fmt.Println("Let's use a slice of Men and see what happens")
    x := make([]Men, 3)
    //These elements are of different types that satisfy the Men interface
    x[0], x[1], x[2] = paul, sam, mike

    for _, value := range x{
        value.SayHi()
    }
}
```

输出是： `This is Mike, a Student: Hi, I am Mike you can call me on 222-222-XXX La la la la... November rain This is Tom, an Employee: Hi, I am Sam, I work at Things Ltd.. Call me on 444-222-XXX La la la la... Born to be wild Let’s use a slice of Men and see what happens Hi, I am Paul you can call me on 111-222-XXX Hi, I am Sam, I work at Golang Inc.. Call me on 444-222-XXX Hi, I am Mike you can call me on 222-222-XXX`

你可能已经注意到，接口类型是一组抽象的方法集，他本身并不实现方法或者精确描述数据结构和方法的实现方式。接口类型只是说：“兄弟，我实现了这些方法，我能胜任”。

值得注意的是这些数据类型没有提及任何的关于接口的信息（我的理解是 Student 和 Employee 数据类型），方法签名的实现部分也没有包含给定的接口类型的信息。

同样的，一个接口类型也不会去关心到底是什么数据类型实现了他自身，看看 Men 接口没有涉及 Student 和 Employee 的信息就明白了。接口类型的本质就是如果一个数据类型实现了自身的方法集，那么该接口类型变量就能够引用该数据类型的值。

**The case of the empty interface**

空接口类型 interface{} 一个方法签名也不包含，所以**所有的数据类型都实现了该方法**。

空接口类型在描述一个对象实例的行为上力不从心，但是当我们需要存储任意数据类型的实例的时候，空接口类型的使用使得我们得心应手。

```
// a is an empty interface variable
var a interface{}
var i int = 5
s := "Hello world"
// These are legal statements
a = i
a = s
```

如果一个函数的参数包括空接口类型 interface{}，实际上函数是在说 “兄弟，我接受任何数据”。如果一个函数返回一个空接口类型，那么函数再说 “我也不确定返回什么，你只要知道我一定返回一个值就好了”。

是不是很有用处？请接着看。

**Functions with interface parameters**

以上的例子给我们展示了一个接口类型如何存储满足他的的数据类型实例，并且展示给我们如何创建存储不同数据类型实例的集合。

利用此思想，我们还可以让函数来接受满足特定接口类型的数据类型实例。

举例来说，我们已经知道 fmt.Print 是一个可变参数的函数，他可以接受任意数量的参数。但是你有没有注意到，有时候我们使用的是 strings、ints 和 floats？

事实上，如果你深入去看 fmt 包，你就会看到如下的接口声明：

```
//The Stringer interface found in fmt package
type Stringer interface {
     String() string
}
```

任何数据类型，只要实现了 Stringer 接口，就能够传递给 fmt.Print 函数，然后打印出该类型 String() 函数的返回值。

让我们试一下：

```
package main
import (
    "fmt"
    "strconv" //for conversions to and from string
)

type Human struct {
    name string
    age int
    phone string
}

//Returns a nice string representing a Human
//With this method, Human implements fmt.Stringer
func (h Human) String() string {
    //We called strconv.Itoa on h.age to make a string out of it.
    //Also, thank you, UNICODE!
    return "❰"+h.name+" - "+strconv.Itoa(h.age)+" years -  ✆ " +h.phone+"❱"
}

func main() {
    Bob := Human{"Bob", 39, "000-7777-XXX"}
    fmt.Println("This Human is : ", Bob)
}
```

输出是

```
This Human is : ❰Bob - 39 years - ✆ 000-7777-XXX❱
```

现在回头看一下我们怎么使用 fmt.Print，我们传递给他参数 Bob，Bob 是一个 Human 类型的实例，然后 Bob 就被优雅的打印出来。我们所做的就是是 Human 实现了 String() 方法。

回想一下 colored boxes example 的例子（这是以前章节的，但是这里我认为不会影响大家的理解）？我们有一个 Color 类型，这个类型实现了 String 方法。我们重新回到那个程序，然后调用 fmt.Print 函数来打印结果：

```
//These two lines do the same thing
fmt.Println("The biggest one is", boxes.BiggestsColor().String())
fmt.Println("The biggest one is", boxes.BiggestsColor())
```

是不是很酷？

另外一个让你喜欢上 interface 接口的例子就是 sort 包，这个包用来对 int、float 和 string 数据类型进行排序。

我们先看一个小例子，然后给你展示一个这个包的神奇之处。

``package main import(“fmt” “sort” )

func main() { // list is a slice of ints. It is unsorted as you can see list := []int {1, 23, 65, 11, 0, 3, 233, 88, 99} fmt.Println(“The list is: “, list)

```
// let's use Ints function that comes in sort
// Ints([]int) sorts its parameter in ibcreasing order. Go read its doc.
sort.Ints(list)
fmt.Println("The sorted list is: ", list) } ``` 输出： ``` The list is: [1 23 65 11 0 3 233 88 99] The sorted list is: [0 1 3 11 23 65 88 99 233] ``` 是不是很简单的工作，但是我想展示的更加吸引人。 事实上，sort包定义了一个包含三个方法签名的接口类型：
```

`type Interface interface { // Len is the number of elements in the collection. Len() int // Less returns whether the element with index i should sort // before the element with index j. Less(i, j int) bool // Swap swaps the elements with indexes i and j. Swap(i, j int) }` ` 在 sort 接口的文档中我们可以看到：

_type, typically a collection, that satisfies sort. Interface can be sorted by the routines in this package. The methods require that the elements of the collection be enumerated by an integer index._

所以我们为了排序一个给定的切片只需要实现这三个函数就可以了！我们来试一下吧：

```
package main
import (
    "fmt"
    "strconv"
    "sort"
)

type Human struct {
    name string
    age int
    phone string
}

func (h Human) String() string {
    return "(name: " + h.name + " - age: "+strconv.Itoa(h.age)+ " years)"
}

type HumanGroup []Human //HumanGroup is a type of slices that contain Humans

func (g HumanGroup) Len() int {
    return len(g)
}

func (g HumanGroup) Less(i, j int) bool {
    if g[i].age < g[j].age {
        return true
    }
    return false
}

func (g HumanGroup) Swap(i, j int){
    g[i], g[j] = g[j], g[i]
}

func main(){
    group := HumanGroup{
        Human{name:"Bart", age:24},
        Human{name:"Bob", age:23},
        Human{name:"Gertrude", age:104},
        Human{name:"Paul", age:44},
        Human{name:"Sam", age:34},
        Human{name:"Jack", age:54},
        Human{name:"Martha", age:74},
        Human{name:"Leo", age:4},
    }

    //Let's print this group as it is
    fmt.Println("The unsorted group is:")
    for _, v := range group{
        fmt.Println(v)
    }

    //Now let's sort it using the sort.Sort function
    sort.Sort(group)

    //Print the sorted group
    fmt.Println("\nThe sorted group is:")
    for _, v := range group{
        fmt.Println(v)
    }
}
```

输出：

```
The unsorted group is:
(name: Bart - age: 24 years)
(name: Bob - age: 23 years)
(name: Gertrude - age: 104 years)
(name: Paul - age: 44 years)
(name: Sam - age: 34 years)
(name: Jack - age: 54 years)
(name: Martha - age: 74 years)
(name: Leo - age: 4 years)

The sorted group is:
(name: Leo - age: 4 years)
(name: Bob - age: 23 years)
(name: Bart - age: 24 years)
(name: Sam - age: 34 years)
(name: Paul - age: 44 years)
(name: Jack - age: 54 years)
(name: Martha - age: 74 years)
(name: Gertrude - age: 104 years)
```

搞定了，如我们所预料的那样。

我们没有实现 HumanGroup 的排序函数，所做的只是实现了三个函数（Len，Less 和 Swap），这个就是 sort.Sort 函数需要的全部信息。

我知道你很奇怪，你很想知道这个神奇之处是怎么实现的。实际上他的实现很简单，Sort 包的排序函数接受任意类型的参数，只要他实现了 Sort 接口类型。

我们尝试了几种不同的利用接口类型作为参数的例子，这些例子利用接口类型达到了抽象数据类型的目的。

我们接下来尝试一下，写一个接受特定接口类型的函数来验证一下我们是否理解了 Interface 类型。

**Our own example**

我们过去使用过 Max(s []int) int 和 Older(s []Person) Person 函数。他们都实现了相似的功能。实际上，实现一个切片的最大值就在做一件事：迭代处理和比较。

让我们尝试一下：

```
package main
import (
    "fmt"
    "strconv"
)

//A basic Person struct
type Person struct {
    name string
    age int
}

//Some slices of ints, floats and Persons
type IntSlice []int
type Float32Slice []float32
type PersonSlice []Person

type MaxInterface interface {
    // Len is the number of elements in the collection.
    Len() int
    //Get returns the element with index i in the collection
    Get(i int) interface{}
    //Bigger returns whether the element at index i is bigger that the j one
    Bigger(i, j int) bool
}

//Len implementation for our three types
func (x IntSlice) Len() int {return len(x)}
func (x Float32Slice) Len() int {return len(x)}
func (x PersonSlice) Len() int {return len(x)}

//Get implementation for our three types
func(x IntSlice) Get(i int) interface{} {return x[i]}
func(x Float32Slice) Get(i int) interface{} {return x[i]}
func(x PersonSlice) Get(i int) interface{} {return x[i]}

//Bigger implementation for our three types
func (x IntSlice) Bigger(i, j int) bool {
    if x[i] > x[j] { //comparing two int
        return true
    }
    return false
}

func (x Float32Slice) Bigger(i, j int) bool {
    if x[i] > x[j] { //comparing two float32
        return true
    }
    return false
}

func (x PersonSlice) Bigger(i, j int) bool {
    if x[i].age > x[j].age { //comparing two Person ages
        return true
    }
    return false
}

//Person implements fmt.Stringer interface
func (p Person) String() string {
    return "(name: " + p.name + " - age: "+strconv.Itoa(p.age)+ " years)"
}

/*
 Returns a bool and a value
 - The bool is set to true if there is a MAX in the collection
 - The value is set to the MAX value or nil, if the bool is false
*/
func Max(data MaxInterface) (ok bool, max interface{}) {
    if data.Len() == 0{
        return false, nil //no elements in the collection, no Max value
    }
    if data.Len() == 1{ //Only one element, return it alongside with true
        return true, data.Get(1)
    }
    max = data.Get(0)//the first element is the max for now
    m := 0
    for i:=1; i<data.Len(); i++ {
        if data.Bigger(i, m){ //we found a bigger value in our slice
            max = data.Get(i)
            m = i
        }
    }
    return true, max
}

func main() {
    islice := IntSlice {1, 2, 44, 6, 44, 222}
    fslice := Float32Slice{1.99, 3.14, 24.8}
    group := PersonSlice{
        Person{name:"Bart", age:24},
        Person{name:"Bob", age:23},
        Person{name:"Gertrude", age:104},
        Person{name:"Paul", age:44},
        Person{name:"Sam", age:34},
        Person{name:"Jack", age:54},
        Person{name:"Martha", age:74},
        Person{name:"Leo", age:4},
    }

    //Use Max function with these different collections
    _, m := Max(islice)
    fmt.Println("The biggest integer in islice is :", m)
    _, m = Max(fslice)
    fmt.Println("The biggest float in fslice is :", m)
    _, m = Max(group)
    fmt.Println("The oldest person in the group is:", m)
}
```

输出：

```
The biggest integer in islice is : 222
The biggest float in fslice is : 24.8
The oldest person in the group is: (name: Gertrude - age: 104 years)
```

MaxInterface 接口包含三个方法签名，满足该接口的数据类型需要实现这三个方法。 1. Len() int: 必须返回集合数据结构的长度 2. Get(int i) interface{}: 必须返回一个在索引 i 的数据元素 3. Bigger(i, j int) bool: 返回位于索引 i 和 j 的数值比较结果 这个排序方式的实现是不是很简单直接。 值得注意的是 Max 方法并没有要求任何关于具体数据类型参数的信息。我们利用接口类型 MaxInterface 实现了数据抽象。

好了，就先到这里吧，再见！

Til next time,  
at 00:00

![](http://zuozuohao.github.io/images/scribble3.png)