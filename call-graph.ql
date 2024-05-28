import java

// to change the method it accesses simply change the name of Method()
class CurrMethod extends Method {

    CurrMethod() {
        this = Method()
    }

    predicate goodName(string methodName) {
        this.getName() = methodName
    }

}

from CurrMethod cm, Method m
where cm.goodName("insertName") and cm.getFile() = m.getFile()
select m, "These are the methods in the same file"