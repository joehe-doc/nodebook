> 本文由 [简悦 SimpRead](http://ksria.com/simpread/) 转码， 原文地址 https://segmentfault.com/a/1190000006914183

**注意:** 前一节我们的代理是对对象进行了代理，而`spring` 的`AOP` 可以基于方法进行代理，因为类的属性和方法都有相应的类来描述或者对应 属性由 java 的 Field 表示，方法由`Method` 来表示

**这里说几个 spring AOP 的接口或类**

1 切入点
-----

`org.springframework.aop.Pointcut`用来说明是对哪些类的哪些方法进行横切, 就是被代理的对象的一个集合

```
public interface Pointcut{
    //说明对哪些类进行横切
    ClassFilter getClassFilter();
    //用来说明对哪些方法进行横切
    MethodMatcher getMethodMatcher();

    Pointcut TRUE = TruePointcut.INSTANCE;
}
```

2 连接点
-----

`org.springframework.aop.JoinPoint` 当程序运行时，对某一个具体的要被横切的方法的描述，通过它可以获取被横切，也就是被代理的那个方法的运行时的状态，例如，被代理的方法的参数，所属对象，所属对象签名，代理对象。

```
public interface JoinPoint {
    //...
    //获取所属对象    
    Object getTarget();

    //获取被代理的方法的参数
    Object[] getArgs();

    //获取连接点的签名
    Signature getSignature();

    //描述位置，哪一行
    SourceLocation getSourceLocation();

    //...
}
```

3 通知
----

`MethodBeforeAdvice,AfterReturningAdvice,ThrowsAdvice， Advice`是对  
附加方法 (被代理的方法前后需要执行的) 的描述  
**3.1**

```
public interface MethodBeforeAdvice extends BeforeAdvice {

    void before(Method method, Object[] args, Object target) throws Throwable;

}
```

**方法说明:**`before`方法有三个参数 被增强的方法，参数，被横切的对象从理论上来说在`before`的方法内部可以执行 `method.invoke(target,args)` 来执行被增强的方法，但是我们一般不会这么做，我们会用这三个参数来动态获取一些信息，或其它功能，但不是去执行被增强的方法，也就是说 **BeforeAdvice 没有代理的职责**。

**接口说明:**`BeforeAdvice`继承`Advice`，`BeforeAdvice` 和 `Advice`都是标识接口 没有方法，没有属性  
参数说明:`method` 具体的一个连接点 `args` 连接点的参数 `target` 连接点所属的对象

**3.2**

```
public interface AfterReturningAdvice extends AfterAdvice {

    void afterReturning(Object returnValue, Method method, Object[] args, Object target) throws Throwable;

}
```

**这里同样没有代理的职责**

**接口说明:**`AfterAdvice`继承`Advice`，都是标识接口 没有方法，没有属性  
**参数说明:**`returnValue`被代理的方法的返回值的描述 `method` 具体的一个连接点 `args` 连接点的参数 `target` 连接点所属的对象  
**3.3**

```
public interface ThrowsAdvice extends AfterAdvice {

}
```

public void afterThrowing(Exception ex)  
public void afterThrowing(RemoteException)  
public void afterThrowing(Method method, Object[] args, Object target, Exception ex)  
public void afterThrowing(Method method, Object[] args, Object target, ServletException ex)

**说明:**`ThrowsAdvice`没有方法，没有属性，但是实现这个接口的类必须有 `afterThrowing` 方法

4 拦截器
-----

`MethodInterceptor`方法拦截器， 继承了`Interceptor`接口，`Interceptor`接口又继承了`Advice`接口，`Interceptor`和`Advice`都是标识接口没有属性和方法

```
public interface MethodInterceptor extends Interceptor {
    
    Object invoke(MethodInvocation invocation) throws Throwable;
}
```

这里的`invoke`方法有代理的责任，也就是说在`invoke`方法内部会调用代理的那个方法，也就是去执行连接点  
`MethodInvocation`继承了`Invocation`接口，`Invocation`接口继承了`Joinpoint`接口，注意这里是`Joinpoint`，是`java`语言的`java.lang.reflect.AccessibleObject.Pointcut`而`Joinpoint`接口内部有 `Object proceed() throws Throwable`这样一个方法，调用这个方法会执行 JoinPoint 描述的那个被代理的方法。

5 配置器
-----

`Advisor`是`Pointcut`和`Advice`的配置器，将 某个具体的 `Advice` 注入到 `Pointcut`所指定的位置

```
public interface Advisor {

    Advice getAdvice();

    boolean isPerInstance();

}

public class DefaultPointcutAdvisor extends AbstractGenericPointcutAdvisor implements Serializable {
    private Pointcut pointcut = Pointcut.TRUE;

    //...
    public DefaultPointcutAdvisor(Pointcut pointcut, Advice advice) {
        this.pointcut = pointcut;
        setAdvice(advice);
    }
    //...
}

public abstract class AbstractGenericPointcutAdvisor extends AbstractPointcutAdvisor {

    private Advice advice;


    /**
     * Specify the advice that this advisor should apply.
     */
    public void setAdvice(Advice advice) {
        this.advice = advice;
    }

    @Override
    public Advice getAdvice() {
        return this.advice;
    }

}
```

从上面我们可以看到`DefaultPointcutAdvisor`需要持有一个`Advice`的对象一个`Pointcut`的对象我们在使用的时候只需要为它提供这两个对象他就会去自己进行配置

6 代理工厂
------

`ProxyFactoryBean`， 创建代理对指定的某个类的对象进行代理，或者对符合规则的一堆类进行代理使用时只需进行配置。