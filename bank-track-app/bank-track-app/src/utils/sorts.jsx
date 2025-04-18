export const balanceSort = (a, b) => {
    if (a.reference_date > b.reference_date) {
        return -1;
    }
    else if (a.reference_date < b.reference_date) {
        return 1;
    }
    else if (a.reference_date === b.reference_date) {
        if (a.balance_type === "expected") {
            return 1;
        }
        else {
            return -1;
        }
    }
    return 0;
}

export const mostRecentBalance = (balances) => {
    return balances.reduce((a, b) => {
        const dateA = new Date(a.reference_date);
        const dateB = new Date(b.reference_date);

        if (dateA > dateB) {
            return a;
        }
        else if (dateA < dateB) {
            return b;
        }
        else if (+dateA === +dateB) {
            if (a.balance_type === "expected") {
                return a;
            }
            else {
                return b;
            }
        }

    });
}
