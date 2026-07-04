import React, { useState } from "react";
import axios from "axios";
import "./getSearch.css";

export default function GetSearch() {

    const [query, setQuery] = useState("");

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const [result, setResult] = useState<any>(null);

    const [companies, setCompanies] = useState<any[]>([]);

    const loadingMessages = [
        "Reading your search request...",
        "Searching GST registration records...",
        "Checking business information...",
        "Validating registration details...",
        "Organizing available GST data...",
        "Preparing your GST report..."
    ];

    const [loadingText, setLoadingText] = useState(loadingMessages[0]);
    
    const fetchGSTDetails = async (gstin: string) => {

    setLoading(true);

    setLoadingText(loadingMessages[0]);

    let index = 0;

    const interval = setInterval(() => {

        index = (index + 1) % loadingMessages.length;

        setLoadingText(loadingMessages[index]);

    }, 1800);

    setCompanies([]);

    setResult(null);

    setError("");

    try {

        const response = await axios.get(

            "http://127.0.0.1:8000/api/search/",

            {

                params: {

                    query: gstin

                }

            }

        );

        setResult(response.data);

    }

    catch {

        setError("Unable to fetch GST Details.");

    }

    finally {

        clearInterval(interval);

        setLoading(false);

    }

};

    const handleSearch = async (e: React.FormEvent) => {

        e.preventDefault();

        setError("");
        setResult(null);
        setCompanies([]);

       if (query.trim() === "") {

    setError("Please enter GSTIN or Company Name.");

    return;

}

        setLoading(true);

        setLoadingText(loadingMessages[0]);

        let index = 0;

        const interval = setInterval(() => {

            index = (index + 1) % loadingMessages.length;

            setLoadingText(loadingMessages[index]);

        }, 1800);

        try {

            const response = await axios.get(
                "http://127.0.0.1:8000/api/search/",
                {
                    params: {
                        query: query
                    }
                }
            );

            console.log(response.data);

            if (response.data.status === "company_list") {

    setCompanies(response.data.companies);

}

else if (response.data.status === "success") {

    setResult(response.data);

}
else {

    setError(response.data.message);

}

        }

        catch (err) {

            console.log(err);

            setError("Unable to fetch GST Details.");

        }

        finally {

            clearInterval(interval);

            setLoading(false);

        }

    };

    return (

        <div className="container">

            <div className="card">

                <h1>GST Intelligence Search</h1>

                <p className="subtitle">

                    Search GSTIN or business name and view verified registration details.

                </p>

                <form onSubmit={handleSearch}>

                    <input

                        type="text"

                        placeholder="Search GSTIN or Company Name"

                        value={query}

                        onChange={(e) =>
    setQuery(e.target.value)
}
                    />

                    <button type="submit">

                        Search

                    </button>

                </form>

            </div>

            {loading && (

                <div className="loading">

                    <div className="spinner"></div>

                    <h3>{loadingText}</h3>

                    <p>Please wait while we retrieve GST information.</p>

                </div>

            )}

            {error && (

                <div className="errorCard">

                    ❌ {error}

                </div>

            )}

           {companies.length > 0 && (

<div className="resultCard">

    <h2>🏢 {companies.length} Matching Businesses Found</h2>

    <p className="companySubtitle">

        Choose the correct business to retrieve complete GST details.

    </p>

    <div className="companyList">

        {companies.map((company, index) => (

            <div
                key={index}
                className="companyCard"
            >

                <div className="companyInfo">

                    <h3>🏢 {company.business_name}</h3>

                    <p>📍 {company.state}</p>

                    <p>

                        <strong>GSTIN</strong>

                        <br />

                        {company.gstin}

                    </p>

                </div>

               <button
    onClick={() => fetchGSTDetails(company.gstin)}
>

    View Complete GST Profile →

</button>

            </div>

        ))}

    </div>

</div>

)}

{result && result.status === "success" && (

<div className="dashboard">

    
    <div className="section">

        <h2>🏢 Business Information</h2>

        <div className="grid">

            <div>
                <span>GSTIN</span>
                <p>{result.data.gstin}</p>
            </div>

            <div>
                <span>Business Name</span>
                <p>{result.data.business_name || "-"}</p>
            </div>

            <div>
                <span>Legal Name</span>
                <p>{result.data.legal_name || "-"}</p>
            </div>

            <div>
                <span>Status</span>

                <p className={
                    result.data.gst_status === "Active"
                    ? "active"
                    : "inactive"
                }>

                    {result.data.gst_status}

                </p>

            </div>

        </div>

    </div>

    <div className="section">

        <h2>📅 Registration Details</h2>

        <div className="grid">

            <div>

                <span>Registration Date</span>

                <p>{result.data.registration_date || "-"}</p>

            </div>

            <div>

                <span>Last Updated</span>

                <p>{result.data.last_updated || "-"}</p>

            </div>

            <div>

                <span>Constitution</span>

                <p>{result.data.constitution || "-"}</p>

            </div>

            <div>

                <span>Taxpayer Type</span>

                <p>{result.data.taxpayer_type || "-"}</p>

            </div>

        </div>

    </div>

    <div className="section">

        <h2>📍 Business Address</h2>

        <div className="grid">

            <div className="fullWidth">

                <span>Principal Address</span>

                <p>{result.data.principal_place || "-"}</p>

            </div>

            <div>

                <span>State</span>

                <p>{result.data.state || "-"}</p>

            </div>

            <div>

                <span>District</span>

                <p>{result.data.district || "-"}</p>

            </div>

            <div>

                <span>Center Jurisdiction</span>

                <p>{result.data.center_jurisdiction || "-"}</p>

            </div>

            <div>

                <span>State Jurisdiction</span>

                <p>{result.data.state_jurisdiction || "-"}</p>

            </div>

            <div>

                <span>Nature Of Business</span>

                <p>{result.data.nature_of_business || "-"}</p>

            </div>

        </div>

    </div>

    
</div>

)}
            

        </div>

    );

}
