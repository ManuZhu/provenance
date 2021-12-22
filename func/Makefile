all:
	g++ -I usr/local/include/ -o databaseInstall databaseInstall.cpp -lhiredis
	g++ -I usr/local/include/ -o computeSI computeSI.cpp -lhiredis
	g++ -I usr/local/include/ -o labelPropagation labelPropagation.cpp -lhiredis
	g++ -I usr/local/include/ -o provenanceToVector provenanceToVector.cpp -lhiredis

clean: