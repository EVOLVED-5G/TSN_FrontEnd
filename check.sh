echo "Errors:"
echo "--------------------------------------------------------------------------------"
docker exec TSN_FrontEnd bash -c "cat ./error.log"
echo ""
echo "Publisher details:"
echo "--------------------------------------------------------------------------------"
docker exec TSN_FrontEnd bash -c "cat ./capif_data/publisherDetails.txt"
echo "[END]"
