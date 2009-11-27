# $dotat: unifdef/Makefile,v 1.15 2009/11/27 17:30:39 fanf2 Exp $

SOURCES=	Makefile README release.sh unifdef.1 unifdef.c unifdefall.sh
TARGETS=	Changelog unifdef unifdef.txt

all: ${TARGETS}

test: unifdef
	./runtests.sh tests

release: ${TARGETS}
	./release.sh

clean:
	rm -rf unifdef-*
	rm -f ${TARGETS} index.html
	rm -f tests/*.out tests/*.err tests/*.rc

realclean: clean
	rm -f *~ .#* *.orig *.core

unifdef: unifdef.c

Changelog: ${SOURCES}
	cvslog >Changelog

unifdef.txt: unifdef.1
	nroff -Tascii -man unifdef.1 | sed -e 's/.//g' >unifdef.txt
