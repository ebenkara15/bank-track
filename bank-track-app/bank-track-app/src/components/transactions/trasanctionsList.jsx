import TransactionCard from "./transactionCard";


const TransactionsList = ({ transactions, allCategories }) => {
    return (
        transactions.length > 0 ? transactions.map(transac => (
            <TransactionCard key={transac.transaction_id} transaction={transac} allCategories={allCategories} />
        )) : "No transactions available."
    );
};

export default TransactionsList;
