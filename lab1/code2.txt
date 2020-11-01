#ifndef PROJECT_META_H
#define PROJECT_META_H

class Meta {
private:
    int a = 0;
    Meta *meta;
public:
    Meta() {
    }
    void set_a(int b, int c) {
        this->a = b + c;
    }
};
#endif //PROJECT_META_H
