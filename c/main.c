
#include <stdio.h>
#include "fe25519.h"
#include "sc25519.h"
#include "ge25519.h"

void dump_ge(const ge25519 *e) {
    unsigned char e_out[32];
    ge25519_pack(e_out, e);
    for (int i=0; i < 32; i++)
        printf("%02x", e_out[i]);
    printf("\n");
}

void scalar(sc25519 *out, unsigned int b) {
    if (b > 255)
        printf("NONO\n");
    unsigned char x[] = { b,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0 };
    sc25519_from32bytes(out, x);
}

void scalarmult_base(ge25519 *out, unsigned int b) {
    sc25519 s;
    scalar(&s, b);
    ge25519_scalarmult_base(out, &s);
}

void scalarmult(ge25519 *out, const ge25519 *in, unsigned int b) {
    ge25519 ge_zero;
    sc25519 zero, one, sc_b;
    scalar(&zero, 0);
    scalar(&one, 1);
    scalar(&sc_b, b);
    ge25519_scalarmult_base(&ge_zero, &zero);
    ge25519_double_scalarmult_vartime(out, in, &sc_b, in, &zero);
}

void add(ge25519 *out, const ge25519 *a, const ge25519 *b) {
    sc25519 one;
    scalar(&one, 1);
    ge25519_double_scalarmult_vartime(out, a, &one, b, &one);
}


void print_scalarmult_base(unsigned int b) {
    ge25519 e;
    scalarmult_base(&e, b);
    printf("B*%d: ", b);
    dump_ge(&e);
}

int main(int argc, char *argv[]) {
    unsigned int a,b;
    ge25519 ea, eb, out;
    for (a=0; a < 10; a++) {
        print_scalarmult_base(a);
    }
    for (a=0; a < 10; a++) {
        scalarmult_base(&ea, a);
        for(b=0; b<3; b++) {
            scalarmult(&out, &ea, b);
            printf("B*%d *%d: ", a, b);
            for (int i=0; i < a*b; i++)
                printf(" ");
            dump_ge(&out);
        }
    }

    /*for (a=0; a < 10; a++) {
        scalarmult_base(&ea, a);
        for(b=0; b<3; b++) {
            scalarmult_base(&eb, b);
            add(&out, &ea, &eb);
            printf(" %d+%d: ", a, b);
            for (int i=0; i < a+b; i++)
                printf(" ");
            dump_ge(&out);
        }
    }*/

    /*
    sc25519 s;
    unsigned char x[] = { 1,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0 };
    sc25519_from32bytes(&s, x);
    printf("sc25519_from32bytes: ");
    for (int i=0; i < 32; i++)
        printf("%02x ", s.v[i]);
    printf("\n");

    printf("sc25519_window3: ");
    signed char r2[85];
    sc25519_window3(r2, &s);
    for (int i=0; i < 85; i++)
        printf("%02x ", r2[i]);
    printf("\n");

    printf("ge25519_scalarmult_base: ");
    ge25519 e;
    ge25519_scalarmult_base(&e, &s);
    unsigned char e_out[32];
    ge25519_pack(e_out, &e);
    for (int i=0; i < 32; i++)
        printf("%02x ", e_out[i]);
    printf("\n");
    */
}
